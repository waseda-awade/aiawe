from datetime import timedelta

from django.utils import timezone


def get_today_date_range():
    """
    Returns the start and end datetime for the current local day.

    Returns:
        tuple: (today_start, today_end) datetime objects in local timezone
    """
    now = timezone.localtime(timezone.now())
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    return today_start, today_end


def mask_api_key(content: str) -> str:
    """
    Masks API keys in error messages etc.
    Looks for patterns like 'sk-*' and replaces the it with 'sk-[MASKED]'
    """
    import re

    # Match sk- followed by any characters until a space, quote, or end of string
    pattern = r"(sk-[a-zA-Z0-9]+)"
    return re.sub(pattern, "sk-[MASKED]", str(content))
