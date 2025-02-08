from django.apps import apps
from django.contrib.admin import SimpleListFilter


class CourseFilterBase(SimpleListFilter):
    """Base filter for filtering by course, either directly or through created_by."""

    title = "Course"  # Display name of the filter

    def lookups(self, request, model_admin):
        Course = apps.get_model("users", "Course")
        if request.user.is_superuser:
            courses = Course.objects.all()
        else:
            # Get courses user has created or manages
            courses = Course.objects.accessible_by_user(request.user)
        return [(c.course_name, c.course_name) for c in courses]

    def queryset(self, request, queryset):
        if self.value():
            filter_path = self.parameter_name
            return queryset.filter(**{filter_path: self.value()})
        return queryset


class CreatorCourseListFilter(CourseFilterBase):
    """Filter that looks up course through the created_by relationship."""

    parameter_name = "created_by__course__course_name"


class CourseListFilter(CourseFilterBase):
    """Filter that looks up course directly."""

    parameter_name = "course__course_name"


class UserListFilter(SimpleListFilter):
    title = "User"
    parameter_name = "created_by"

    def lookups(self, request, model_admin):
        User = apps.get_model("users", "User")
        if request.user.is_superuser:
            users = User.objects.all()
        else:
            users = [
                request.user,
                *list(User.objects.accessible_by_user(request.user)),
            ]

        return [(user.username, user.name) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_by__username=self.value())
        return queryset
