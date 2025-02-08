from io import BytesIO

import pandas as pd
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import FileResponse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import truncatechars
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from openpyxl import Workbook

from awe_system_ui.core.filters import CourseListFilter
from awe_system_ui.core.mixins import AccessControlAdminMixin
from awe_system_ui.llm_caller.forms import BatchProcessingForm
from awe_system_ui.llm_caller.tasks import process_batch

from .models import APIKey
from .models import APIRequest
from .models import BatchItem
from .models import BatchProcessing
from .models import BatchProcessingQuota
from .models import LLMConfig
from .models import LLMModel
from .models import QuotaConfig


@admin.register(QuotaConfig)
class QuotaConfigAdmin(admin.ModelAdmin):
    list_display = ["model", "daily_limit", "created_at", "updated_at"]
    list_filter = ["model"]


@admin.register(APIRequest)
class APIRequestAdmin(AccessControlAdminMixin, admin.ModelAdmin):
    list_display = [
        "created_by",
        "get_course",
        "status",
        "get_model_name",
        "get_truncated_essay",
        "score",
        "get_truncated_reasoning",
        "get_truncated_error",
        "created_at",
    ]
    list_filter = ["status", "model", CourseListFilter]
    search_fields = [
        "essay",
        "result",
        "created_by__email",
        "created_by__course__course_name",
    ]
    actions = ["export_as_csv"]

    @admin.display(description="Essay")
    def get_truncated_essay(self, obj):
        return truncatechars(obj.essay, 50)

    @admin.display(description="Reasoning")
    def get_truncated_reasoning(self, obj):
        return truncatechars(obj.reasoning, 50)

    @admin.display(description="Error")
    def get_truncated_error(self, obj):
        return truncatechars(obj.error, 50)

    @admin.display(description="Course", ordering="created_by__course")
    def get_course(self, obj):
        return obj.created_by.course if obj.created_by.course else "-"

    @admin.display(description="Model", ordering="model__display_name")
    def get_model_name(self, obj):
        return obj.model.display_name

    def has_add_permission(self, request):
        """Disable add permission for APIRequestAdmin"""
        return False

    @admin.action(
        description="Export selected requests as Excel",
    )
    def export_as_csv(self, request, queryset):
        field_names = [
            "created_at",
            "status",
            "created_by__email",
            "created_by__course__course_id",
            "created_by__course__course_name",
            "model__name",
            "essay",
            "score",
            "reasoning",
            "error",
            "result",
        ]

        # Create workbook and select active sheet
        workbook = Workbook()
        worksheet = workbook.active

        # Write header
        headers = [
            "Timestamp",
            "Status",
            "User Email",
            "Course ID",
            "Course Name",
            "LLM Model",
            "Essay",
            "Score",
            "Reasoning",
            "Error",
            "Raw Response",
        ]
        worksheet.append(headers)

        # Write data rows
        for obj in queryset:
            row = []
            for field in field_names:
                value = obj
                for attr in field.split("__"):
                    value = getattr(value, attr, None)
                    if value is None:
                        break

                # Format timestamp if it's the created_at field
                if field == "created_at" and value is not None:
                    value = timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S %Z")

                row.append(value if value is not None else "")
            worksheet.append(row)

        # Save to buffer
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)

        # Create the HttpResponse
        now = timezone.localtime().strftime("%Y%m%d_%H%M%S")
        filename = f"Requests_{now}.xlsx"

        response = HttpResponse(
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "name",
        "url",
        "llm_type",
        "order",
        "is_default",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_active", "is_default", "llm_type"]
    search_fields = ["name", "display_name"]
    ordering = ["order"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "display_name",
                    "name",
                    "llm_type",
                    "url",
                ),
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "order",
                    "is_default",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = [
        "target_llm_model",
        "is_active",
        "system_prompt",
        "user_prompt_template",
        "temperature",
        "updated_at",
    ]
    list_filter = ["target_llm_model", "is_active", "created_at"]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = [
        "model",
        "masked_key",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_active", "model"]
    search_fields = ["model__display_name"]
    ordering = ["created_at"]

    @admin.display(
        description="API Key",
    )
    def masked_key(self, obj):
        """Show only the last 4 characters of the key."""
        return f"...{obj.key[-4:]}" if obj.key else ""


@admin.register(BatchProcessingQuota)
class BatchProcessingQuotaAdmin(admin.ModelAdmin):
    list_display = ["model", "daily_limit", "created_at", "updated_at"]
    list_filter = ["model"]


@admin.register(BatchProcessing)
class BatchProcessingAdmin(AccessControlAdminMixin, admin.ModelAdmin):
    form = BatchProcessingForm
    readonly_fields = [
        "model",
        "essay_field_name",
        "status",
        "input_file",
        "output_file",
        "created_at",
        "updated_at",
        "task_id",
    ]

    def get_list_display(self, request):
        list_display = [
            "model",
            "get_download_link",
            "get_items_count",
            "status",
            "created_at",
        ]
        if request.user.is_superuser:
            list_display = ["created_by", *list_display]
        return list_display

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/download/",
                self.admin_site.admin_view(self.download_view),
                name="llm_caller_batchprocessing_download",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Add the upload button to the changelist view"""
        extra_context = extra_context or {}
        return super().changelist_view(request, extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        """Replace the default add view to handle the batch upload form"""
        if not self.has_add_permission(request):
            raise PermissionDenied

        if request.method == "POST":
            form = BatchProcessingForm(request.POST, request.FILES)
            if form.is_valid():
                batch = form.save(commit=False)
                batch.created_by = request.user
                df_data = pd.read_excel(batch.input_file, keep_default_na=False)
                # Check quota
                quota = BatchProcessingQuota.objects.filter(model=batch.model).first()
                if not quota:
                    # Create a default quota for this model if none exists
                    quota = BatchProcessingQuota.objects.create(
                        model=batch.model,
                    )
                remaining = quota.get_remaining_quota(request.user) if quota else 0
                if remaining < df_data.shape[0]:
                    msg = (
                        f"Daily batch processing quota exceeded. Remaining: {remaining}"
                    )
                    messages.error(request, msg)
                else:
                    try:
                        batch.save()

                        # Create batch items
                        items = []
                        for _, row in df_data.iterrows():
                            items.append(
                                BatchItem(
                                    batch=batch,
                                    essay=row[batch.essay_field_name],
                                    row_data=row.to_dict(),
                                ),
                            )
                        BatchItem.objects.bulk_create(items)

                        # Start processing
                        transaction.on_commit(lambda: process_batch.delay(batch.id))
                        messages.success(request, "Batch processing started")
                        return HttpResponseRedirect(
                            reverse("admin:llm_caller_batchprocessing_changelist"),
                        )
                    except (ValueError, TypeError) as e:
                        messages.error(request, f"Error processing file: {e}")
        else:
            form = BatchProcessingForm()

        context = {
            **self.admin_site.each_context(request),
            "title": "Create Batch Processing",
            "form": form,
            "has_view_permission": self.has_view_permission(request),
            IS_POPUP_VAR: request.GET.get(IS_POPUP_VAR, ""),
        }
        return TemplateResponse(
            request,
            "admin/llm_caller/batchprocessing/batch_request_creation.html",
            context,
        )

    def download_view(self, request, object_id):
        batch = get_object_or_404(BatchProcessing, pk=object_id)

        # Check if user has permission to download
        if not (request.user.is_superuser or batch.created_by == request.user):
            msg = "You don't have permission to download this file."
            raise PermissionDenied(msg)

        if not batch.output_file:
            messages.error(request, "Output file not available")
            return HttpResponseRedirect(
                reverse("admin:llm_caller_batchprocessing_changelist"),
            )

        return FileResponse(
            batch.output_file.open("rb"),
            as_attachment=True,
            filename=batch.output_file.name.split("/")[-1],
        )

    @admin.display(description="Download")
    def get_download_link(self, obj):
        if obj.output_file:
            url = reverse("admin:llm_caller_batchprocessing_download", args=[obj.pk])
            return format_html('<a href="{}">Download</a>', url)
        return "-"

    @admin.display(description="Items")
    def get_items_count(self, obj):
        return obj.items.count()


@admin.register(BatchItem)
class BatchItemAdmin(admin.ModelAdmin):
    list_display = [
        "batch",
        "status",
        "score",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status", "batch"]
    search_fields = ["essay", "reasoning", "error"]
