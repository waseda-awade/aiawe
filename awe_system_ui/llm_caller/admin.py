from django.contrib import admin

from .models import APIRequest
from .models import LLMConfig
from .models import LLMModel
from .models import QuotaConfig


@admin.register(QuotaConfig)
class QuotaConfigAdmin(admin.ModelAdmin):
    list_display = ["model", "daily_limit", "created_at", "updated_at"]
    list_filter = ["model"]


@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "status",
        "get_model_name",
        "essay",
        "score",
        "created_at",
    ]
    list_filter = ["status", "user", "model"]
    search_fields = ["essay", "result"]

    @admin.display(
        description="Model",
        ordering="model__display_name",
    )
    def get_model_name(self, obj):
        return obj.model.display_name


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "display_name",
        "name",
        "is_default",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_active", "is_default"]
    search_fields = ["name", "display_name"]
    ordering = ["order"]


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = [
        "system_prompt",
        "user_prompt_template",
        "temperature",
        "updated_at",
    ]
    list_filter = ["created_at"]
