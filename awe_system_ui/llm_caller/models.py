import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class QuotaConfig(models.Model):
    daily_limit = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "created_at"

    def __str__(self):
        return f"QuotaConfig(daily_limit={self.daily_limit})"

    @classmethod
    def get_default_quota(cls):
        try:
            # First try to get the latest quota config
            return cls.objects.latest()
        except cls.DoesNotExist:
            # If no quota exists, create a default one
            return cls.objects.create(daily_limit=10)


class APIRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    essay = models.TextField()
    result = models.TextField(blank=True, default="")  # Keep for raw response
    score = models.FloatField(null=True, blank=True)  # New field for parsed score
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

    def __str__(self):
        return f"APIRequest(user={self.user}, status={self.status}, \
            essay={self.essay[:20]})"


class LLMModel(models.Model):
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
    )  # display name (e.g., "GPT-3.5 Turbo")
    is_active = models.BooleanField(
        default=False,
        help_text="The most recently created active model will be used",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.display_name} ({'Active' if self.is_active else 'Inactive'})"

    def save(self, *args, **kwargs):
        # If this model is being set as active, deactivate all others
        if self.is_active:
            LLMModel.objects.exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_model(cls):
        try:
            return cls.objects.get(is_active=True)
        except cls.DoesNotExist:
            # Get or create a default model
            return cls.objects.get_or_create(
                name="gpt-3.5-turbo",
                defaults={
                    "display_name": "GPT-3.5 Turbo",
                    "is_active": True,
                },
            )[0]


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
        get_latest_by = "created_at"

    def __str__(self):
        return f"LLM Config (Updated: {self.updated_at})"

    @classmethod
    def get_active_config(cls):
        try:
            return cls.objects.latest()
        except cls.DoesNotExist:
            return cls.objects.create()

    def clean(self):
        # This ensures validation runs even when saving through admin
        validate_user_prompt_template(self.user_prompt_template)
