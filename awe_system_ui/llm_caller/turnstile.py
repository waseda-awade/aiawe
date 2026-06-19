import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(token: str, remoteip: str | None = None) -> bool:
    """POST to Cloudflare Turnstile and return True only on confirmed success.

    Fails closed: any network error, timeout, or unexpected response returns False.
    """
    try:
        response = requests.post(
            _SITEVERIFY_URL,
            data={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": token,
                "remoteip": remoteip,
            },
            timeout=5,
        )
        return response.json().get("success") is True
    except Exception:
        logger.exception("Turnstile verification request failed")
        return False
