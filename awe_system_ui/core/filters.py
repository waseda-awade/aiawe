from django.apps import apps
from django.contrib.admin import SimpleListFilter


class CourseListFilter(SimpleListFilter):
    title = "Course"  # Display name of the filter
    parameter_name = "course__course_name"  # URL parameter

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
            return queryset.filter(course__course_name=self.value())
        return queryset
