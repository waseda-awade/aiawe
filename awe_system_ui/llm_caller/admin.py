from django.contrib import admin

from .models import APIRequest
from .models import LLMConfig
from .models import LLMModel
from .models import QuotaConfig


@admin.register(QuotaConfig)
class QuotaConfigAdmin(admin.ModelAdmin):
    list_display = ["daily_limit", "created_at", "updated_at"]


@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "essay", "score", "created_at"]
    list_filter = ["status", "user"]
    search_fields = ["essay", "result"]


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = ["display_name", "name", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "display_name"]


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = [
        "system_prompt",
        "user_prompt_template",
        "temperature",
        "updated_at",
    ]
    list_filter = ["created_at"]
