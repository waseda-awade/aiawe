import time
from pathlib import Path

from django.conf import settings


def get_storage_usage():
    """Get the total size in Bytes of all files in the media directory."""
    media_root = Path(settings.MEDIA_ROOT)
    total_size = 0
    for item in media_root.rglob("*"):
        if item.is_file():
            total_size += item.stat().st_size
    return total_size


def delete_media_files_older_than(days_ago: int = 30):
    """Delete all files in the media directory older than the given number of days."""
    count = 0
    media_root = Path(settings.MEDIA_ROOT)
    for item in media_root.rglob("*"):
        if item.is_file():
            if item.stat().st_mtime < time.time() - days_ago * 86400:
                item.unlink()
                count += 1
    return count
