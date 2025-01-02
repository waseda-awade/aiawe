import openai
from celery import shared_task
from django.conf import settings
from pydantic import BaseModel

from .models import APIRequest

client = openai.OpenAI()


class EssayScore(BaseModel):
    score: float


@shared_task
def process_openai_request(request_id, model_name, temperature, prompt_template):
    try:
        api_request = APIRequest.objects.get(id=request_id)

        if settings.FAKE_LLM_REQUEST:
            api_request.result = '{"score": 4.0}'
            api_request.score = 4.0
            api_request.status = "COMPLETED"
            api_request.save()
        else:
            # Format prompt using template
            formatted_prompt = prompt_template.format(essay=api_request.essay)

            # Make request to OpenAI with configured settings
            response = client.beta.chat.completions.parse(
                model=model_name,
                messages=[
                    {"role": "user", "content": formatted_prompt},
                ],
                temperature=temperature,
                response_format=EssayScore,
            )

            # Store raw response
            result = response.choices[0].message.content
            api_request.result = result

            # Store parsed result
            parsed_result = response.choices[0].message.parsed
            api_request.score = parsed_result.score
            api_request.status = "COMPLETED"

            api_request.save()

    except (openai.OpenAIError, KeyError, ValueError) as e:
        api_request.status = "FAILED"
        api_request.error = str(e)
        api_request.save()
