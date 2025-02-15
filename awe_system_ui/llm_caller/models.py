import re

from celery.app import app_or_default
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import URLValidator
from django.core.validators import validate_email
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from awe_system_ui.core.mixins import AccessControlManagerMixin
from awe_system_ui.core.mixins import AccessControlMixin
from awe_system_ui.core.models import TaskTimestampedBase
from awe_system_ui.core.models import TimestampedBase

from .utils import format_datetime
from .utils import get_today_date_range

User = get_user_model()


QUOTA_USAGE_STATUS = ["PENDING", "PROCESSING", "COMPLETED"]


class LLMModel(TimestampedBase):
    LLM_TYPE_CHOICES = [
        ("openai", "OpenAI"),
        ("third_party", "Third Party"),
    ]

    order = models.IntegerField(
        default=10,
        help_text="Order of the model in the UI (smaller number comes first)",
    )
    name = models.CharField(
        max_length=200,
        help_text=(
            "The model name for calling the LLM API (e.g., gpt-4o-2024-11-20)."
            " Check <a href='https://platform.openai.com/docs/models#current-model-aliases'"
            " target='_blank'>OpenAI model list</a>."
        ),
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Display name for the model (e.g., GPT-4o)",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="This model will be pre-selected in the UI",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active models will be listed in the UI",
    )
    llm_type = models.CharField(
        max_length=20,
        choices=LLM_TYPE_CHOICES,
        default="openai",
        help_text="The type of LLM service to use",
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        help_text=(
            "URL for third-party LLM service "
            "(e.g., http://host.docker.internal:8080/v1). "
            "Leave empty for OpenAI."
        ),
        validators=[URLValidator()],
    )

    class Meta:
        ordering = ["order"]
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.display_name} ({'Active' if self.is_active else 'Inactive'})"

    def save(self, *args, **kwargs):
        # If this model is being set as default, reset all others
        if self.is_default:
            LLMModel.objects.exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_models(cls):
        return cls.objects.filter(is_active=True)

    def get_used_quota(self, user) -> int:
        """Get the number of completed requests for today for this model and user."""
        today_start, today_end = get_today_date_range()

        # Calculate the number of completed requests for today
        # status is either PENDING or COMPLETED
        return APIRequest.objects.filter(
            created_by=user,
            model=self,
            status__in=QUOTA_USAGE_STATUS,
            created_at__range=(today_start, today_end),
        ).count()

    def check_quota(self, user) -> bool:
        """
        Check if the user has exceeded their quota for this model.
        Returns True if the user has exceeded their quota, False otherwise.
        """
        try:
            quota_config = self.quota_config
        except QuotaConfig.DoesNotExist:
            # No quota config means unlimited requests
            return True

        used_quota = self.get_used_quota(user)
        return used_quota < quota_config.daily_limit

    def clean(self):
        super().clean()
        if self.llm_type == "third_party" and not self.url:
            raise ValidationError(
                {"url": "URL is required for third-party LLM services"},
            )


class QuotaConfig(TimestampedBase):
    model = models.OneToOneField(
        LLMModel,
        on_delete=models.CASCADE,
        related_name="quota_config",
        help_text="The LLM model this quota applies to",
    )
    daily_limit = models.IntegerField(
        default=10,
        help_text="Maximum number of requests per day for this model",
    )

    class Meta:
        get_latest_by = "created_at"

    def __str__(self):
        return f"QuotaConfig({self.model.display_name}, limit={self.daily_limit})"


class APIRequestManager(AccessControlManagerMixin, models.Manager):
    def extend_manager_query(self, query, user):
        query |= Q(created_by__course__managers=user) | Q(
            created_by__course__created_by=user,
        )
        return query


class APIRequest(AccessControlMixin, TaskTimestampedBase):
    essay_topic = models.TextField(blank=True, default="")
    essay = models.TextField()
    model = models.ForeignKey(
        LLMModel,
        on_delete=models.PROTECT,
        related_name="requests",
        help_text="The LLM model used for this request",
    )
    result = models.TextField(blank=True, default="")
    score = models.FloatField(null=True, blank=True)
    reasoning = models.TextField(blank=True, default="")
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
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ],
        default="PENDING",
    )
    task_id = models.CharField(max_length=100, blank=True, default="")
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag - True means this request is deleted",
    )

    objects = APIRequestManager()

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            (
                "can_manage_limited_apirequests",
                "Can manage API requests with limited visibility",
            ),
        ]

    def __str__(self):
        return f"APIRequest(created_by={self.created_by}, status={self.status}, \
            model={self.model.display_name}, essay={self.essay[:20]})"


def validate_user_prompt_template(value):
    """Validate that the template contains only the allowed placeholders."""
    allowed_placeholders = {"{essay}", "{essay_topic}"}
    placeholders = {m.group() for m in re.finditer(r"{[^}]+}", value)}
    invalid_placeholders = placeholders - allowed_placeholders
    if invalid_placeholders:
        msg = (
            f"Invalid placeholders: {invalid_placeholders}. "
            f"Only {allowed_placeholders} are allowed."
        )
        raise ValidationError(msg)
    if "{essay}" not in placeholders:
        msg = "Template must contain {essay} placeholder"
        raise ValidationError(msg)


class LLMConfig(TimestampedBase):
    target_llm_model = models.ForeignKey(
        LLMModel,
        on_delete=models.CASCADE,
        related_name="configs",
        help_text="The LLM model this configuration applies to",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only one config can be active per model",
    )
    system_prompt = models.TextField(
        help_text="The system prompt instructs the model to generate JSON format.",
        default=settings.DEFAULT_SYSTEM_PROMPT,
    )
    user_prompt_template = models.TextField(
        help_text=(
            "Use '{essay}' (without the quote) as placeholder for user input<br>"
            "Use '{essay_topic}' (without the quote) as placeholder for the essay topic"
        ),
        default=settings.DEFAULT_USER_PROMPT_TEMPLATE,
        validators=[validate_user_prompt_template],
    )
    temperature = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(2.0),
        ],
        help_text="Value between 0 and 2",
    )

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "created_at"

    def __str__(self):
        return f"LLM Config for {self.target_llm_model.display_name}"

    def save(self, *args, **kwargs):
        # If this config is being set as active,
        #  deactivate all others for the same model
        if self.is_active:
            LLMConfig.objects.filter(
                target_llm_model=self.target_llm_model,
            ).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_config(cls, model_name):
        """Get the active config for the specified model."""
        try:
            return cls.objects.get(
                target_llm_model__name=model_name,
                is_active=True,
            )
        except cls.DoesNotExist:
            # Create a default config for this model
            model = LLMModel.objects.get(name=model_name)
            return cls.objects.create(target_llm_model=model)

    def clean(self):
        # This ensures validation runs even when saving through admin
        validate_user_prompt_template(self.user_prompt_template)


class APIKey(TimestampedBase):
    model = models.ForeignKey(
        LLMModel,
        on_delete=models.CASCADE,
        related_name="api_keys",
        help_text="The LLM model this key is associated with",
    )
    key = models.CharField(
        max_length=255,
        help_text="API Key (e.g., OpenAI starts with 'sk-')",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active keys will be used",
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return (
            f"{self.model.display_name} API Key "
            f"({'Active' if self.is_active else 'Inactive'})"
        )

    @classmethod
    def get_available_key(
        cls,
        model_id: int,
        default_key: str | None = None,
    ) -> str | None:
        """Get the first available active key for the specified model."""
        obj = (
            cls.objects.filter(
                model__id=model_id,
                is_active=True,
            )
            .order_by("created_at")
            .first()
        )
        if not obj:
            return default_key
        return obj.key


class BatchProcessingQuota(TimestampedBase):
    """Quota configuration for batch processing."""

    model = models.ForeignKey(
        LLMModel,
        on_delete=models.CASCADE,
        related_name="batch_quotas",
    )
    daily_limit = models.IntegerField(
        default=100,
        help_text="Maximum number of batch requests allowed per day",
    )

    class Meta:
        verbose_name_plural = "Batch processing quotas"

    def __str__(self):
        return f"BatchQuota({self.model.display_name}, limit={self.daily_limit})"

    def get_remaining_quota(self, user):
        """Get remaining quota for the user."""
        today_start, today_end = get_today_date_range()
        used_today = BatchItem.objects.filter(
            batch__created_by=user,
            batch__model=self.model,
            batch__created_at__range=(today_start, today_end),
            status__in=QUOTA_USAGE_STATUS,
        ).count()
        return max(0, self.daily_limit - used_today)


class BatchProcessingManager(AccessControlManagerMixin, models.Manager):
    pass


class BatchProcessing(AccessControlMixin, TaskTimestampedBase):
    """Model for batch processing requests."""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("ABORTED", "Aborted"),
    ]

    model = models.ForeignKey(
        LLMModel,
        on_delete=models.PROTECT,
        related_name="batch_requests",
    )
    essay_topic_field_name = models.CharField(
        max_length=50,
        default="Essay Topic",
        help_text="Column name containing the essay topics in the Excel file",
    )
    essay_field_name = models.CharField(
        max_length=50,
        default="Essay",
        help_text="Column name containing the essays in the Excel file",
    )
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

    objects = BatchProcessingManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Batch processing requests"
        permissions = [
            (
                "can_manage_limited_batchprocessings",
                "Can manage batch processing requests with limited visibility",
            ),
        ]

    def __str__(self):
        return f"Batch({self.id}, {self.model.display_name}, {self.status})"

    @property
    def items_failure_error(self):
        if self.items.filter(status="FAILED").count() == 0:
            return ""
        msg = "These items failed to process:"
        for idx, item in enumerate(self.items.all().order_by("created_at")):
            if item.status == "FAILED":
                msg += f"\n- Item #{idx+1}: {item.error or 'Unknown error'}"
        return msg

    def notify_completion(self):
        """Send email notification when batch processing is complete."""
        if not getattr(settings, "NOTIFY_BATCH_COMPLETION", True):
            return

        if not self.created_by:
            return

        try:
            validate_email(self.created_by.email)
        except ValidationError:
            return

        success_count = self.items.filter(status="COMPLETED").count()
        failure_count = self.items.filter(status="FAILED").count()

        subject = "[AiAWE] Batch Processing "
        if self.status == "FAILED":
            subject += "Failed"
            error_msg = f"\nError:\n{self.error}"
            if self.error_details:
                error_msg += f"\n\nError Details:\n{self.error_details}"
            error_msg += "\n"
        else:
            subject += "Completed"
            error_msg = ""

        relative_url = reverse(
            "admin:llm_caller_batchprocessing_download",
            args=[self.pk],
        )
        download_url = f"{settings.SITE_URL.rstrip('/')}{relative_url}"
        context = {
            "batch": self,
            "download_url": download_url,
            "success_count": success_count,
            "failure_count": failure_count,
            "total_count": self.items.count(),
            "error_msg": error_msg,
        }

        text_message = render_to_string(
            "admin/llm_caller/batch_completion_email.txt",
            context,
        )

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.created_by.email],
        )

    def get_batch_items_as_rows(self):
        """Get the batch items as a list of dict data."""
        rows = []
        for item in self.items.all().order_by("created_at"):
            row = item.row_data.copy()
            row.update(
                {
                    "Status": item.status,
                    "Score": item.score,
                    "Reasoning": item.reasoning,
                    "Error": item.error,
                    "Raw Response": item.result,
                    "Created At": format_datetime(item.created_at),
                    "Started At": format_datetime(item.started_at),
                    "Ended At": format_datetime(item.ended_at),
                },
            )
            rows.append(row)
        return rows

    def stop_processing(self):
        """Stop the batch processing and all its item tasks."""
        if self.status not in ["PENDING", "PROCESSING"]:
            return False

        app = app_or_default()

        # Revoke the main batch task
        if self.task_id:
            app.control.revoke(self.task_id, terminate=True)

        for item in self.items.filter(status__in=["PENDING", "PROCESSING"]):
            item.status = "ABORTED"
            item.error = "Processing was stopped by user"
            item.ended_at = timezone.now()
            item.save()

        self.status = "ABORTED"
        self.error = "Processing was stopped by user"
        self.ended_at = timezone.now()
        self.save()
        return True


class BatchItem(TaskTimestampedBase):
    """Individual items in a batch processing request."""

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("ABORTED", "Aborted"),
    ]

    batch = models.ForeignKey(
        BatchProcessing,
        on_delete=models.CASCADE,
        related_name="items",
    )
    essay_topic = models.TextField(blank=True, default="")
    essay = models.TextField()
    result = models.TextField(blank=True, default="")
    score = models.FloatField(null=True, blank=True)
    reasoning = models.TextField(blank=True, default="")
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    row_data = models.JSONField(
        help_text="Original row data from input file",
    )
    task_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"BatchItem({self.batch.id}, {self.status})"


@receiver(pre_delete, sender=BatchProcessing)
def stop_batch_on_delete(sender, instance, **kwargs):
    """Stop batch processing when the batch is deleted."""
    instance.stop_processing()
