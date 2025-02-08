import contextlib

from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.db import transaction
from django.db.models import CharField
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from awe_system_ui.core.mixins import AccessControlManagerMixin
from awe_system_ui.core.mixins import AccessControlMixin


class CourseManager(AccessControlManagerMixin, models.Manager):
    pass


class Course(AccessControlMixin, models.Model):
    course_id = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=200)

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


class CustomUserManager(AccessControlManagerMixin, UserManager):
    def extend_manager_query(self, query, user):
        """Include students in courses managed by the user or created by the user."""
        query |= Q(course__managers=user) | Q(course__created_by=user)
        return query


class User(AccessControlMixin, AbstractUser):
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

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=False, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    required_fields = ["email", "name", "username"]

    def __str__(self):
        return f"{self.name} <{self.email}>"

    class Meta:
        permissions = [
            ("can_manage_limited_users", "Can manage users with limited visibility"),
        ]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def save(self, *args, **kwargs):
        """Override save to sync email with EmailAddress."""
        email_changed = False
        if self.pk:  # If this is an existing user
            with contextlib.suppress(User.DoesNotExist):
                old_user = User.objects.get(pk=self.pk)
                if old_user.email != self.email:
                    email_changed = True

        with transaction.atomic():
            super().save(*args, **kwargs)

            if email_changed:
                # Update or create primary email address
                EmailAddress.objects.update_or_create(
                    user=self,
                    primary=True,
                    defaults={
                        "email": self.email,
                        "verified": True,  # Set new email to verified
                    },
                )
                # Delete any other email addresses for this user
                EmailAddress.objects.filter(user=self).exclude(
                    email=self.email,
                ).delete()
