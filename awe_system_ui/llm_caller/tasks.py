import os

import openai
from celery import shared_task
from django.conf import settings

from .models import APIRequest

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)


@shared_task
def process_openai_request(request_id):
    try:
        api_request = APIRequest.objects.get(id=request_id)

        if settings.FAKE_LLM_REQUEST:
            api_request.result = "OK."
            api_request.status = "COMPLETED"
            api_request.save()
        else:
            # Make request to OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": api_request.prompt},
                ],
            )

            # Update the request with the result
            api_request.result = response.choices[0].message.content
            api_request.status = "COMPLETED"
            api_request.save()

    # https://platform.openai.com/docs/guides/error-codes
    except openai.OpenAIError as e:
        api_request.status = "FAILED"
        api_request.error = str(e)
        api_request.save()
