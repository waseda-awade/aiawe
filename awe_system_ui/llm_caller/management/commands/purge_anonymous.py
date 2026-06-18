from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from awe_system_ui.llm_caller.models import APIRequest


class Command(BaseCommand):
    help = "Delete anonymous APIRequest rows (created_by=NULL) older than N hours."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Delete rows older than this many hours (default: 24).",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        cutoff = timezone.now() - timedelta(hours=hours)
        qs = APIRequest.objects.filter(
            created_by__isnull=True,
            created_at__lt=cutoff,
        )
        count, _ = qs.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {count} anonymous request(s) older than {hours}h.",
            ),
        )
