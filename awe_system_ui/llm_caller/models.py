import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import URLValidator
from django.db import models

from .utils import get_today_date_range

User = get_user_model()


class LLMModel(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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

        return APIRequest.objects.filter(
            user=user,
            model=self,
            status="COMPLETED",
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


class QuotaConfig(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "created_at"

    def __str__(self):
        return f"QuotaConfig({self.model.display_name}, limit={self.daily_limit})"


class APIRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    error = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ],
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=100, blank=True, default="")
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag - True means this request is deleted",
    )

    def __str__(self):
        return f"APIRequest(user={self.user}, status={self.status}, \
            model={self.model.display_name}, essay={self.essay[:20]})"


def validate_user_prompt_template(value):
    # Count occurrences of {essay}
    essay_count = value.count("{essay}")
    if essay_count < 1:
        msg = "Did you forget to include a '{essay}' placeholder?"
        raise ValidationError(
            msg,
        )

    # Check for any other placeholders using regex
    # This will find anything like {word} or {word_word} except {essay}
    other_placeholders = re.findall(r"(?<!{){(?!essay})[^{}]+}(?!})", value)
    if other_placeholders:
        msg = (
            f"Template contains invalid placeholders: {', '.join(other_placeholders)}. "
            "Only '{essay}' is allowed."
        )
        raise ValidationError(
            msg,
        )


class LLMConfig(models.Model):
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
        help_text="Use '{essay}' (without the quote) as placeholder for user input",
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class OpenAIKey(models.Model):
    key = models.CharField(
        max_length=255,
        help_text="OpenAI API Key (starts with 'sk-')",
    )
    name = models.CharField(
        max_length=100,
        help_text="A name to identify this key (e.g., 'Primary Key', 'Backup Key')",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active keys will be used",
    )
    order = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Keys with lower order values will be used first",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "OpenAI API Key"
        verbose_name_plural = "OpenAI API Keys"

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

    @classmethod
    def get_available_key(cls):
        """Get the first available active key."""
        return cls.objects.filter(is_active=True).order_by("order").first()
