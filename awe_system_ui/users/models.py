from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CourseManager(models.Manager):
    def accessible_by_user(self, user):
        """Returns queryset of courses that the user can access."""
        if not user or not user.is_authenticated:
            return self.none()
        if user.is_superuser:
            return self.all()
        return self.filter(
            models.Q(created_by=user) | models.Q(managers=user),
        ).distinct()


class Course(models.Model):
    course_id = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses",
    )

    objects = CourseManager()

    class Meta:
        ordering = ["course_id"]
        permissions = [
            (
                "can_manage_limited_courses",
                "Can manage courses with limited visibility",
            ),
        ]

    def __str__(self):
        return f"{self.course_id}: {self.course_name}"


class CustomUserManager(UserManager):
    def accessible_by_user(self, user):
        """Returns queryset of users that the user can access."""
        if user.is_superuser:
            return self.all()
        return self.filter(
            models.Q(created_by=user) | models.Q(course__in=user.managed_courses.all()),
        ).distinct()


class User(AbstractUser):
    """
    Default custom user model for AWE.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    objects = CustomUserManager()

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The course this student belongs to",
    )

    managed_courses = models.ManyToManyField(
        Course,
        related_name="managers",
        blank=True,
        help_text="Courses that this user manages.",
    )

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_users",
    )

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=False, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def __str__(self):
        return f"{self.name} <{self.email}>"

    class Meta:
        permissions = [
            ("can_add_limited_users", "Can add users with limited visibility"),
        ]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
