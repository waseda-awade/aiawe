import logging
import time
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
from typing import Literal

import openai
import pandas as pd
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from pydantic import BaseModel

from .models import APIKey
from .models import APIRequest
from .models import BatchProcessing
from .models import LLMConfig
from .utils import format_datetime
from .utils import mask_api_key

logger = logging.getLogger(__name__)


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
        except APIRequest.DoesNotExist as e:
            try:
                self.retry(countdown=2**self.request.retries)
            except MaxRetriesExceededError:
                msg = f"APIRequest with id {request_params.request_id} not found"
                logger.exception(msg)
                raise ValueError(msg) from e

        api_request.task_id = self.request.id

        if settings.FAKE_LLM_REQUEST:
            api_request.result = (
                '{"score": 4.0, "reasoning": "This is a fake response"}'
            )
            api_request.score = 4.0
            api_request.reasoning = "This is a fake response"
            api_request.status = "COMPLETED"
            api_request.save()
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
        response = client.chat.completions.create(
            model=request_params.model_name,
            messages=[
                {"role": "system", "content": request_params.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=request_params.temperature,
            response_format={"type": "json_object"},
        )

        # Extract and parse response manually
        result = response.choices[0].message.content
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
        api_request.save()
    except (openai.OpenAIError, KeyError, ValueError) as e:
        api_request.status = "FAILED"
        api_request.error = mask_api_key(str(e))
        if e.__context__:
            api_request.error_details = mask_api_key(str(e.__context__))
        api_request.save()
        return False
    else:
        return True


@shared_task(bind=True)
def process_batch(
    self,
    batch_id: int,
):
    """Process a batch of essays."""
    try:
        batch = BatchProcessing.objects.get(id=batch_id)
        batch.status = "PROCESSING"
        batch.task_id = self.request.id
        batch.save()

        # Process each item
        for item in batch.items.filter(status="PENDING"):
            item.status = "PROCESSING"
            item.task_id = self.request.id
            item.save()

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

                # Process with OpenAI
                client = get_openai_client(
                    model_id=batch.model.id,
                    llm_type=batch.model.llm_type,
                    base_url=batch.model.url,
                )
                response = client.chat.completions.create(
                    model=llm_params.model_name,
                    messages=[
                        {"role": "system", "content": llm_params.system_prompt},
                        {
                            "role": "user",
                            "content": llm_params.user_prompt_template.format(
                                essay=item.essay,
                            ),
                        },
                    ],
                    temperature=llm_params.temperature,
                    response_format={"type": "json_object"},
                )

                # Parse response
                result = response.choices[0].message.content
                item.result = result
                parsed_result = EssayEvaluation.model_validate_json(result)
                item.score = parsed_result.score
                item.reasoning = parsed_result.reasoning
                item.status = "COMPLETED"

            except (openai.OpenAIError, ValueError, TypeError) as e:
                item.status = "FAILED"
                item.error = mask_api_key(str(e))
                if e.__context__:
                    item.error_details = mask_api_key(str(e.__context__))

            item.save()

        # Create output file
        if batch.items.exclude(status="COMPLETED").exists():
            batch.status = "FAILED"
        else:
            batch.status = "COMPLETED"
            create_output_file(batch)
            batch.notify_completion()

        batch.save()

    except (ValueError, TypeError):
        batch.status = "FAILED"
        batch.save()


def create_output_file(batch):
    """Create output Excel file for completed batch."""
    # Collect all data
    rows = []
    for item in batch.items.all():
        row = item.row_data.copy()
        row.update(
            {
                "Timestamp": format_datetime(item.created_at),
                "Status": item.status,
                "Score": item.score,
                "Reasoning": item.reasoning,
                "Error": item.error,
                "Raw Response": item.result,
            },
        )
        rows.append(row)

    # Create Excel file
    df_data = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_data.to_excel(writer, index=False)

    # Save to storage
    filename = (
        f"batch_output_{batch.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    path = f"batch_outputs/{timezone.now().strftime('%Y/%m/%d')}/{filename}"
    default_storage.save(path, ContentFile(output.getvalue()))
    batch.output_file = path
    batch.save()


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
