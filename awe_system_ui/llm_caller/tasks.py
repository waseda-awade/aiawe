import openai
from celery import shared_task
from django.conf import settings
from pydantic import BaseModel

from .models import APIRequest

client = openai.OpenAI()


class EssayScore(BaseModel):
    score: float


@shared_task
def process_openai_request(
    request_id,
    model_name,
    temperature,
    system_prompt,
    user_prompt_template,
):
    try:
        api_request = APIRequest.objects.get(id=request_id)

        if settings.FAKE_LLM_REQUEST:
            api_request.result = '{"score": 4.0}'
            api_request.score = 4.0
            api_request.status = "COMPLETED"
            api_request.save()
            return

        # Format prompt using the provided template
        user_prompt = user_prompt_template.format(essay=api_request.essay)

        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        # Extract and parse response manually
        result = response.choices[0].message.content
        api_request.result = result
        # Assuming the older models return JSON-like content that can be parsed
        try:
            parsed_result = EssayScore.model_validate_json(result)
            api_request.score = parsed_result.score
        except ValueError as e:
            msg = "Failed to parse response from model"
            raise ValueError(msg) from e

        api_request.status = "COMPLETED"
        api_request.save()

    except (openai.OpenAIError, KeyError, ValueError) as e:
        api_request.status = "FAILED"
        api_request.error = str(e)
        api_request.save()
