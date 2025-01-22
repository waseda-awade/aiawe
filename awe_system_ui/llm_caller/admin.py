import csv
from datetime import datetime

from django.contrib import admin
from django.http import HttpResponse

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
        "get_course",
        "status",
        "get_model_name",
        "essay",
        "score",
        "created_at",
    ]
    list_filter = ["status", "user", "model", "user__course"]
    search_fields = ["essay", "result", "user__email", "user__course__course_name"]
    actions = ["export_as_csv"]

    @admin.display(description="Course", ordering="user__course")
    def get_course(self, obj):
        return obj.user.course if obj.user.course else "-"

    @admin.display(description="Model", ordering="model__display_name")
    def get_model_name(self, obj):
        return obj.model.display_name

    @admin.action(
        description="Export selected requests as CSV",
    )
    def export_as_csv(self, request, queryset):
        field_names = [
            "created_at",
            "user__email",
            "user__course__course_id",
            "user__course__course_name",
            "model__name",
            "essay",
            "score",
            "result",
        ]

        response = HttpResponse(content_type="text/csv")
        now = datetime.now().strftime("%Y%m%d_%H%M%S")  # noqa: DTZ005
        response["Content-Disposition"] = f"attachment; filename=Requests_{now}.csv"
        writer = csv.writer(response)

        # Write header
        writer.writerow(
            [
                "Timestamp",
                "User Email",
                "Course ID",
                "Course Name",
                "LLM Model",
                "Essay",
                "Score",
                "Raw Response",
            ],
        )

        # Write data rows
        for obj in queryset:
            row = []
            for field in field_names:
                value = obj
                for attr in field.split("__"):
                    value = getattr(value, attr, None)
                    if value is None:
                        break
                row.append(value if value is not None else "")
            writer.writerow(row)

        return response


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "name",
        "display_name",
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
