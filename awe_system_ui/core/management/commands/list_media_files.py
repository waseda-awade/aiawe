from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List all files in media directory with their sizes"

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        total_size = 0

        for item in Path(media_root).rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(media_root)
                size = item.stat().st_size
                total_size += size

                # Convert size to MB for readability
                size_mb = size / (1024 * 1024)
                display_path = item.name if relative_path == "." else relative_path

                self.stdout.write(f"{display_path}: {size_mb:.2f} MB")

        self.stdout.write(
            self.style.SUCCESS(f"\nTotal size: {total_size / (1024 * 1024):.2f} MB"),
        )
