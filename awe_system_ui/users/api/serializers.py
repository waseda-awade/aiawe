from dj_rest_auth.models import TokenModel
from rest_framework import serializers

from awe_system_ui.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "name", "email", "role", "url"]
        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TokenModel
        fields = ["key", "created", "user"]
