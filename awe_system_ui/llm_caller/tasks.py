import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Literal
from typing import TypeVar

import openai
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.utils import timezone
from pydantic import BaseModel

from .models import APIKey
from .models import APIRequest
from .models import BatchItem
from .models import BatchProcessing
from .models import LLMConfig
from .utils import mask_api_key

logger = logging.getLogger(__name__)

MyTaskModel = TypeVar("MyTaskModel", bound=BatchItem | BatchProcessing | APIRequest)


def get_openai_client(
    model_id: int,
    llm_type: Literal["openai", "third_party"],
    base_url: str | None = None,
):
    default_key = ""
    match llm_type:
        case "openai":
            default_key = ""
        case "third_party":
            default_key = "dummy"
        case _:
            msg = f"Invalid LLM type: {llm_type}"
            raise ValueError(msg)

    key = APIKey.get_available_key(model_id, default_key=default_key)
    if not key:
        msg = (
            f"No active API key found for llm model {model_id}."
            f" Please add an API key in the admin interface."
        )
        raise ValueError(msg)

    if not base_url:
        # Set it to None (it might be an empty string which will cause an error)
        base_url = None
    return openai.OpenAI(api_key=key, base_url=base_url)


class EssayEvaluation(BaseModel):
    score: float
    reasoning: str


@dataclass
class LLMRequestParams:
    request_id: int
    model_name: str
    temperature: float
    system_prompt: str
    user_prompt_template: str


def call_openai_api(
    client: openai.OpenAI,
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
) -> str:
    """Helper function to make OpenAI API calls.

    Returns:
        str: The raw response content from the model
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


@shared_task(bind=True)
def process_openai_request(
    self,
    request_params_dict: dict,
    delay_seconds=0,
):
    # Convert dict back to dataclass
    request_params = LLMRequestParams(**request_params_dict)

    if delay_seconds > 0:
        msg = f"Delaying LLM request by {delay_seconds} seconds"
        logger.info(msg)
        time.sleep(delay_seconds)

    try:
        try:
            api_request = APIRequest.objects.get(id=request_params.request_id)
            api_request.started_at = timezone.now()
            api_request.save()
        except APIRequest.DoesNotExist as e:
            try:
                self.retry(countdown=2**self.request.retries)
            except MaxRetriesExceededError:
                msg = f"APIRequest with id {request_params.request_id} not found"
                logger.exception(msg)
                raise ValueError(msg) from e

        api_request.task_id = self.request.id

        if _handle_debug_delay_and_fake(api_request, delay_seconds):
            return True

        # Format prompt using the provided template
        user_prompt = request_params.user_prompt_template.format(
            essay=api_request.essay,
        )

        client = get_openai_client(
            model_id=api_request.model.id,
            llm_type=api_request.model.llm_type,
            base_url=api_request.model.url,
        )

        result = call_openai_api(
            client=client,
            model_name=request_params.model_name,
            system_prompt=request_params.system_prompt,
            user_prompt=user_prompt,
            temperature=request_params.temperature,
        )
        api_request.result = result
        # Assuming the older models return JSON-like content that can be parsed
        try:
            parsed_result = EssayEvaluation.model_validate_json(result)
            api_request.score = parsed_result.score
            api_request.reasoning = parsed_result.reasoning
        except ValueError as e:
            msg = "Failed to parse response from model"
            raise ValueError(msg) from e

        api_request.status = "COMPLETED"
        api_request.ended_at = timezone.now()
        api_request.save()
    except (openai.OpenAIError, KeyError, ValueError) as e:
        api_request.status = "FAILED"
        api_request.error = mask_api_key(str(e))
        if e.__context__:
            api_request.error_details = mask_api_key(str(e.__context__))
        api_request.ended_at = timezone.now()
        api_request.save()
        return False
    else:
        return True


def _start_task(item: MyTaskModel, task_id: str):
    item.started_at = timezone.now()
    item.status = "PROCESSING"
    item.task_id = task_id
    item.save()


def _end_task(
    item: MyTaskModel,
    status: Literal["COMPLETED", "FAILED"],
):
    item.ended_at = timezone.now()
    item.status = status
    item.save()


def _handle_debug_delay_and_fake(
    item: MyTaskModel,
    delay_seconds: int,
):
    """Handle debug delay and fake requests.
    Args:
        item: The item to handle
        delay_seconds: The delay in seconds
    Returns:
        bool: True if the item was handled, False otherwise
    """
    if delay_seconds > 0:
        msg = f"Delaying LLM request by {delay_seconds} seconds"
        logger.info(msg)
        time.sleep(delay_seconds)

    if settings.FAKE_LLM_REQUEST:
        if "fail" in item.essay.lower():
            item.error = "This item is a fake failure."
            item.error_details = "This is a fake error details."
            _end_task(item, "FAILED")
        else:
            item.score = 4.0
            item.reasoning = "This is a fake response. " * 40
            _end_task(item, "COMPLETED")
        return True
    return False


@shared_task(bind=True)
def process_batch(
    self,
    batch_id: int,
    delay_seconds=0,
):
    """Process a batch of essays."""
    try:
        batch = BatchProcessing.objects.get(id=batch_id)
        _start_task(batch, self.request.id)

        # Process each item
        for item in batch.items.filter(status="PENDING").order_by("created_at"):
            _start_task(item, self.request.id)

            if _handle_debug_delay_and_fake(item, delay_seconds):
                continue

            try:
                # Get LLM config
                llm_config = LLMConfig.get_active_config(model_name=batch.model.name)
                llm_params = LLMRequestParams(
                    request_id=item.id,
                    model_name=batch.model.name,
                    temperature=llm_config.temperature,
                    system_prompt=llm_config.system_prompt,
                    user_prompt_template=llm_config.user_prompt_template,
                )

                client = get_openai_client(
                    model_id=batch.model.id,
                    llm_type=batch.model.llm_type,
                    base_url=batch.model.url,
                )
                # Process with OpenAI
                result = call_openai_api(
                    client=client,
                    model_name=llm_params.model_name,
                    system_prompt=llm_params.system_prompt,
                    user_prompt=llm_params.user_prompt_template.format(
                        essay=item.essay,
                    ),
                    temperature=llm_params.temperature,
                )
                item.result = result
                parsed_result = EssayEvaluation.model_validate_json(result)
                item.score = parsed_result.score
                item.reasoning = parsed_result.reasoning
                _end_task(item, "COMPLETED")

            except (openai.OpenAIError, ValueError, TypeError) as e:
                item.error = mask_api_key(str(e))
                if e.__context__:
                    item.error_details = mask_api_key(str(e.__context__))
                _end_task(item, "FAILED")

            batch.updated_at = timezone.now()
            batch.save()

        # If there are any items that are not completed, set the batch status to failed
        qs = batch.items.exclude(status="COMPLETED")
        if qs.exists():
            _end_task(batch, "FAILED")
            batch.error = batch.items_failure_error
            batch.save()
        else:
            _end_task(batch, "COMPLETED")

    except SoftTimeLimitExceeded:
        batch.error = "The batch processing timed out."
        _end_task(batch, "FAILED")
    except (ValueError, TypeError) as e:
        batch.error = mask_api_key(str(e))
        if e.__context__:
            batch.error_details = mask_api_key(str(e.__context__))
        _end_task(batch, "FAILED")
    finally:
        # Notify user
        batch.notify_completion()


@shared_task()
def delete_old_batch_processing_files(days_ago: int = 30):
    """Delete files older than the given number of days.
    Parameters:
        days_ago: int = 30
    Returns:
        int: The number of files deleted.
    """

    qs = BatchProcessing.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=days_ago),
    )
    count = 0
    for batch in qs:
        count += batch.delete_files()
    return count
