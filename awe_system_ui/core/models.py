from django.db import models


class TimestampedBase(models.Model):
    """Base model that adds created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TaskTimestampedBase(TimestampedBase):
    """Base model that adds task-related fields and timestamps."""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("ABORTED", "Aborted"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    error = models.TextField(
        blank=True,
        default="",
        help_text="Error message that displays to the user.",
    )
    error_details = models.TextField(
        blank=True,
        default="",
        help_text="Error details to diagnose the error.",
    )

    task_id = models.CharField(max_length=100, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
