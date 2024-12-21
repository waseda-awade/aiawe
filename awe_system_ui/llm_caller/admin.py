from django.contrib import admin

from .models import APIRequest
from .models import QuotaConfig


@admin.register(QuotaConfig)
class QuotaConfigAdmin(admin.ModelAdmin):
    list_display = ["daily_limit", "created_at", "updated_at"]


@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "prompt", "result", "created_at"]
    list_filter = ["status", "user"]
    search_fields = ["prompt", "result"]
