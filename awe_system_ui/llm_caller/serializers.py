from rest_framework import serializers

from .models import APIRequest
from .models import LLMModel


class LLMModelSerializer(serializers.ModelSerializer):
    used_quota = serializers.SerializerMethodField()
    daily_limit = serializers.IntegerField(source="quota_config.daily_limit")

    class Meta:
        model = LLMModel
        fields = [
            "id",
            "order",
            "is_default",
            "display_name",
            "used_quota",
            "daily_limit",
        ]

    def get_used_quota(self, obj):
        try:
            user = self.context["request"].user
        except (KeyError, AttributeError):
            return 0

        if not user.is_authenticated:
            return 0

        return obj.get_used_quota(user)


class APIRequestSerializer(serializers.ModelSerializer):
    model_id = serializers.IntegerField(write_only=True)
    model_display_name = serializers.CharField(
        source="model.display_name",
        read_only=True,
    )

    class Meta:
        model = APIRequest
        fields = [
            "id",
            "essay_topic",
            "essay",
            "score",
            "reasoning",
            "error",
            "status",
            "created_at",
            "model_id",
            "model_display_name",
        ]
        read_only_fields = [
            "score",
            "reasoning",
            "status",
            "created_at",
            "model_display_name",
        ]

    def create(self, validated_data):
        model_id = validated_data.pop("model_id")
        try:
            model = LLMModel.objects.get(id=model_id, is_active=True)
        except LLMModel.DoesNotExist as e:
            raise serializers.ValidationError(
                {"model_id": "Selected model is not supported"},
            ) from e

        return APIRequest.objects.create(
            **validated_data,
            model=model,
        )
