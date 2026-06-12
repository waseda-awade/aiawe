from dj_rest_auth.models import TokenModel
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from awe_system_ui.users.models import Course

UserModel = get_user_model()


class CustomLoginSerializer(LoginSerializer):
    @staticmethod
    def validate_email_verification_status(user, email=None):
        # Skip validation for superusers
        if user.is_superuser:
            return

        # Call parent's static method
        LoginSerializer.validate_email_verification_status(user, email)


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """
    User model w/o password
    """

    class Meta:
        extra_fields = []
        if hasattr(UserModel, "USERNAME_FIELD"):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, "EMAIL_FIELD"):
            extra_fields.append(UserModel.EMAIL_FIELD)
        if hasattr(UserModel, "first_name"):
            extra_fields.append("first_name")
        if hasattr(UserModel, "last_name"):
            extra_fields.append("last_name")
        # Expose staff and superuser flags so clients can adjust UI for admins.
        if hasattr(UserModel, "is_staff"):
            extra_fields.append("is_staff")
        if hasattr(UserModel, "is_superuser"):
            extra_fields.append("is_superuser")
        model = UserModel
        fields = ("pk", *extra_fields)
        read_only_fields = ("email", "is_staff", "is_superuser")


class TokenSerializer(serializers.ModelSerializer):
    user = CustomUserDetailsSerializer()

    class Meta:
        model = TokenModel
        fields = ["key", "created", "user"]


class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(required=True)
    course_id = serializers.CharField(required=False, allow_null=True, max_length=10)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["name"] = self.validated_data.get("name", "")
        return data

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data.get("name")
        user.save()
        return user

    def custom_signup(self, request, user):
        course_id = self.validated_data.get("course_id")
        if course_id:
            try:
                course = Course.objects.get(course_id=course_id)
                user.course = course
                user.save()
            except Course.DoesNotExist as e:
                raise serializers.ValidationError(
                    {"course_id": "Please enter a valid course id"},
                ) from e
