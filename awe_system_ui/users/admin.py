import contextlib

import pandas as pd
from allauth.account.admin import EmailAddressAdmin
from allauth.account.decorators import secure_admin_login
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin import helpers
from django.contrib.auth import admin as auth_admin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .forms import AdminUserRegistrationForm
from .forms import AssignCourseForm
from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .forms import UserBatchUploadForm
from .models import Course
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


class CourseListFilter(SimpleListFilter):
    title = "Course"  # Display name of the filter
    parameter_name = "course__course_name"  # URL parameter

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            courses = Course.objects.all()
        else:
            # Get courses user has created or manages
            courses = Course.objects.accessible_by_user(request.user)
        return [(c.course_name, c.course_name) for c in courses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(course__course_name=self.value())
        return queryset


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    search_fields = [
        "username",
        "email",
        "name",
        "course__course_name",
    ]
    filter_horizontal = ["managed_courses", "groups", "user_permissions"]

    def get_list_display(self, request):
        if request.user.is_superuser:
            return [
                "username",
                "email",
                "name",
                "course",
                "get_managed_courses",
                "created_by",
                "is_staff",
                "is_superuser",
            ]
        return ["username", "email", "name", "course"]

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            fieldsets = (
                (None, {"fields": ("username", "password")}),
                (_("Personal info"), {"fields": ("name", "email", "course")}),
                (
                    _("Course Management"),
                    {
                        "fields": ("managed_courses",),
                        "description": (
                            "Courses that this user can manage."
                            " Course managers can view and"
                            " modify users in their managed courses."
                        ),
                    },
                ),
                (
                    _("Permissions"),
                    {
                        "fields": (
                            "is_active",
                            "is_staff",
                            "is_superuser",
                            "groups",
                            "user_permissions",
                        ),
                    },
                ),
                (
                    _("Meta data"),
                    {"fields": ("created_by", "last_login", "date_joined")},
                ),
            )
        elif request.user.has_perm("users.can_add_limited_users"):
            fieldsets = (
                (None, {"fields": ("username", "password")}),
                (_("Personal info"), {"fields": ("name", "email", "course")}),
            )
        return fieldsets

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return [
                "is_active",
                "is_staff",
                "is_superuser",
                CourseListFilter,
                "created_by",
            ]
        return [CourseListFilter]

    @admin.display(description="Managed Courses")
    def get_managed_courses(self, obj):
        return ", ".join(c.course_id for c in obj.managed_courses.all()) or "-"

    actions = ["assign_course_action"]

    def get_queryset(self, request):
        return self.model.objects.accessible_by_user(request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new user
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.has_perm("users.can_add_limited_users"):
            if obj is None:
                return True
            return (
                obj.created_by == request.user
                or obj.course in request.user.managed_courses.all()
            )
        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Disable the default add user button"""
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "register/",
                self.admin_site.admin_view(self.register_user_view),
                name="user_register",
            ),
            path(
                "batch-upload/",
                self.admin_site.admin_view(self.batch_upload_view),
                name="user_batch_upload",
            ),
        ]
        return custom_urls + urls

    def register_user_view(self, request):
        if request.method == "POST":
            form = AdminUserRegistrationForm(data=request.POST, staff_user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "User registered successfully.")
                return HttpResponseRedirect(reverse("admin:users_user_changelist"))
        else:
            form = AdminUserRegistrationForm(staff_user=request.user)

        context = {
            "form": form,
            "title": "Register New User",
            **self.admin_site.each_context(request),
        }
        return TemplateResponse(request, "admin/users/user/register.html", context)

    def batch_upload_view(self, request):
        if request.method == "POST":
            form = UserBatchUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["file"]
                df_data = pd.read_excel(file, keep_default_na=False)
                success_count = 0
                errors = []

                for idx, row in df_data.iterrows():
                    try:
                        with transaction.atomic():
                            # Convert row to dictionary and handle missing columns
                            row_dict = row.to_dict()

                            # Handle course assignment if present
                            if row_dict.get("course_id"):
                                with contextlib.suppress(Course.DoesNotExist):
                                    row_dict["course"] = Course.objects.get(
                                        course_id=row_dict["course_id"],
                                    )

                            # Create verified email address using form's save method
                            form_data = {
                                "email": row_dict["email"],
                                "password": row_dict["password"],
                                "name": row_dict.get("name"),
                                "username": row_dict.get("username")
                                or row_dict["email"],
                                "course": row_dict.get("course"),
                            }
                            temp_form = AdminUserRegistrationForm(
                                data=form_data,
                                staff_user=request.user,
                            )
                            if temp_form.is_valid():
                                temp_form.save()
                                success_count += 1
                            else:
                                errors.append(
                                    f"Row {idx + 2}: {temp_form.errors.as_text()}",
                                )
                    except (KeyError, ValueError) as e:
                        msg = f"Row {idx + 2}: {e!s}"
                        errors.append(msg)

                if success_count > 0:
                    messages.success(
                        request,
                        f"Successfully created {success_count} users.",
                    )
                if errors:
                    for error in errors:
                        messages.error(request, error)
                return HttpResponseRedirect(reverse("admin:users_user_changelist"))
        else:
            form = UserBatchUploadForm()

        context = {
            "form": form,
            "title": "Batch Upload Users",
            **self.admin_site.each_context(request),
        }
        return TemplateResponse(request, "admin/users/user/batch_upload.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_register_button"] = True
        extra_context["show_batch_upload_button"] = True
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Assign selected users to a course")
    def assign_course_action(self, request, queryset):
        if not self.has_change_permission(request):
            raise PermissionDenied

        # Handle form submission
        if request.POST.get("post"):
            form = AssignCourseForm(data=request.POST, staff_user=request.user)
            if form.is_valid():
                course = form.cleaned_data["course"]
                updated = 0
                for user in queryset:
                    if self.has_change_permission(request, user):
                        user.course = course
                        user.save()
                        updated += 1

                if not course:
                    msg = f"Set empty course for {updated} users"
                else:
                    msg = f"Assigned {updated} users to course: {course.course_name}"
                messages.success(request, msg)
                return None

        else:
            form = AssignCourseForm(staff_user=request.user)

        # If we're allowed to change any of the selected users, show the form
        if not any(self.has_change_permission(request, obj) for obj in queryset):
            raise PermissionDenied

        context = {
            "title": "Assign users to course",
            "queryset": queryset,
            "form": form,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            **self.admin_site.each_context(request),
        }
        return TemplateResponse(
            request,
            "admin/users/user/assign_course.html",
            context,
        )

    def get_form(self, request, obj=None, change=False, **kwargs):  # noqa: FBT002
        form_class = super().get_form(request, obj, **kwargs)
        return lambda *args, **k: form_class(*args, **{**k, "staff_user": request.user})


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = ["course_id", "course_name"]

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return ((None, {"fields": ("course_id", "course_name", "created_by")}),)
        return ((None, {"fields": ("course_id", "course_name")}),)

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ["course_id", "course_name", "created_by", "get_managers"]
        return ["course_id", "course_name", "get_managers"]

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ["created_by"]
        return []

    @admin.display(description="Managers")
    def get_managers(self, obj):
        return ", ".join(user.username for user in obj.managers.all()) or "-"

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new course
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return self.model.objects.accessible_by_user(request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.has_perm("users.can_manage_limited_courses"):
            if obj is None:
                return True
            return obj.created_by == request.user or request.user in obj.managers.all()
        return False

    def has_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.has_perm(
            "users.can_manage_limited_courses",
        )


admin.site.unregister(EmailAddress)


@admin.register(EmailAddress)
class CustomEmailAddressAdmin(EmailAddressAdmin):
    """Customize EmailAddressAdmin to allow delete permission for staff users"""

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.has_perm(
            "users.can_manage_limited_courses",
        )
