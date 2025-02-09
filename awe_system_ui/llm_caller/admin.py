from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import truncatechars
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html

from awe_system_ui.core.filters import CreatorCourseListFilter
from awe_system_ui.core.filters import UserListFilter
from awe_system_ui.core.mixins import AccessControlAdminMixin

from .forms import BatchProcessingForm
from .models import APIKey
from .models import APIRequest
from .models import BatchItem
from .models import BatchProcessing
from .models import BatchProcessingQuota
from .models import LLMConfig
from .models import LLMModel
from .models import QuotaConfig
from .tasks import process_batch
from .utils import format_datetime
from .utils import generate_excel_response


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
    list_filter = ["status", "model", CreatorCourseListFilter, UserListFilter]
    search_fields = [
        "essay",
        "result",
        "created_by__email",
        "created_by__course__course_name",
    ]
    readonly_fields = ["task_id", "created_at", "updated_at", "started_at", "ended_at"]

    actions = ["export_as_excel"]

    # Define field mapping for export
    export_field_mapping = [
        ("status", "Status"),
        ("created_by__name", "User Name"),
        ("created_by__email", "User Email"),
        ("created_by__course__course_id", "Course ID"),
        ("created_by__course__course_name", "Course Name"),
        ("model__name", "LLM Model"),
        ("essay", "Essay"),
        ("score", "Score"),
        ("reasoning", "Reasoning"),
        ("error", "Error"),
        ("result", "Raw Response"),
        ("created_at", "Created At"),
        ("started_at", "Started At"),
        ("ended_at", "Ended At"),
    ]

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
        return (
            obj.created_by.course if obj.created_by and obj.created_by.course else "-"
        )

    @admin.display(description="Model", ordering="model__display_name")
    def get_model_name(self, obj):
        return obj.model.display_name

    def has_add_permission(self, request):
        """Disable add permission for APIRequestAdmin"""
        return False

    @admin.action(description="Export selected requests as Excel")
    def export_as_excel(self, request, queryset):
        rows = []
        # Write data rows
        for obj in queryset:
            row = {}
            for field, header in self.export_field_mapping:
                value = obj
                for attr in field.split("__"):
                    value = getattr(value, attr, None)
                    if value is None:
                        break

                # Format the value if it's a datetime field
                if (
                    field in ["created_at", "started_at", "ended_at"]
                    and value is not None
                ):
                    value = format_datetime(value)

                row.update({header: value})
            rows.append(row)
        return generate_excel_response(rows, "Evaluations")


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
    readonly_fields = ["created_at", "updated_at"]
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
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    ordering = ["order"]


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = [
        "target_llm_model",
        "is_active",
        "system_prompt",
        "user_prompt_template",
        "temperature",
        "created_at",
        "updated_at",
    ]
    list_filter = ["target_llm_model", "is_active", "created_at"]
    readonly_fields = ["created_at", "updated_at"]


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
    readonly_fields = ["created_at", "updated_at"]
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
    readonly_fields = ["created_at", "updated_at"]


@admin.register(BatchProcessing)
class BatchProcessingAdmin(AccessControlAdminMixin, admin.ModelAdmin):
    form = BatchProcessingForm
    readonly_fields = [
        "model",
        "essay_field_name",
        "status",
        "error",
        "error_details",
        "created_at",
        "updated_at",
        "started_at",
        "ended_at",
        "task_id",
    ]
    actions = ["generate_output_file"]

    def get_list_display(self, request):
        list_display = [
            "model",
            "get_download_link",
            "get_items_count",
            "status",
            "get_truncated_error",
            "created_at",
            "started_at",
            "ended_at",
        ]
        if request.user.is_superuser:
            list_display = ["created_by", *list_display]
        return list_display

    @admin.display(description="Error")
    def get_truncated_error(self, obj):
        return truncatechars(obj.error, 50)

    @admin.action(description="Generate output file for selected batches")
    def generate_output_file(self, request, queryset):
        count = 0
        for batch in queryset:
            try:
                batch.create_output_file()
                count += 1
            except (ValueError, TypeError, PermissionError) as e:
                messages.error(
                    request,
                    f"Failed to generate output file for Batch {batch.id}: {e!s}",
                )
        messages.success(request, f"Output file generated for {count} batch(es).")

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
                df_data = form.cleaned_data["df_data"]
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
                        transaction.on_commit(
                            lambda: process_batch.delay(
                                batch.id,
                                delay_seconds=getattr(settings, "TASK_DELAY", 0),
                            ),
                        )
                        messages.success(request, "Batch processing started")
                        return HttpResponseRedirect(
                            reverse("admin:llm_caller_batchprocessing_changelist"),
                        )
                    except (ValueError, TypeError, PermissionError) as e:
                        messages.error(request, f"Error processing file: {e!s}")
        else:
            form = BatchProcessingForm()

        # Pre-calculate quota info
        for model in form.fields["model"].queryset:
            quota = BatchProcessingQuota.objects.filter(model=model).first()
            if quota:
                model.remaining_quota = quota.get_remaining_quota(request.user)
                model.quota_daily_limit = quota.daily_limit
            else:
                model.remaining_quota = "unlimited"
                model.quota_daily_limit = "unlimited"

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

        try:
            rows = batch.get_batch_items_as_rows()
            response = generate_excel_response(rows, "Batch_Evaluations")

        except (ValueError, TypeError) as e:
            messages.error(request, f"Error generating output file: {e!s}")
            return HttpResponseRedirect(
                reverse("admin:llm_caller_batchprocessing_changelist"),
            )
        else:
            return response

    @admin.display(description="Download")
    def get_download_link(self, obj):
        url = reverse("admin:llm_caller_batchprocessing_download", args=[obj.pk])
        return format_html('<a href="{}">Download</a>', url)

    @admin.display(description="Items")
    def get_items_count(self, obj):
        return obj.items.count()


@admin.register(BatchItem)
class BatchItemAdmin(admin.ModelAdmin):
    list_display = [
        "batch",
        "status",
        "get_truncated_essay",
        "get_truncated_reasoning",
        "get_truncated_error",
        "score",
        "created_at",
        "started_at",
        "ended_at",
    ]
    list_filter = ["status", "batch"]
    search_fields = ["essay", "reasoning", "error"]
    readonly_fields = [
        "row_data",
        "task_id",
        "created_at",
        "updated_at",
        "started_at",
        "ended_at",
    ]
    ordering = ["-created_at"]

    @admin.display(description="Essay")
    def get_truncated_essay(self, obj):
        return truncatechars(obj.essay, 50)

    @admin.display(description="Reasoning")
    def get_truncated_reasoning(self, obj):
        return truncatechars(obj.reasoning, 50)

    @admin.display(description="Error")
    def get_truncated_error(self, obj):
        return truncatechars(obj.error, 50)
