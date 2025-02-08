from django.core.management.base import BaseCommand

from awe_system_ui.core.utils import delete_media_files_older_than


class Command(BaseCommand):
    help = "Delete media files older than the specified number of days"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Delete files older than this many days (default: 30)",
        )

    def handle(self, *args, **options):
        days = options["days"]
        count = delete_media_files_older_than(days)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {count} files older than {days} days",
            ),
        )
