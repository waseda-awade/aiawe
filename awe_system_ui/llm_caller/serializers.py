from rest_framework import serializers

from .models import APIRequest


class APIRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequest
        fields = ["id", "essay", "score", "error", "status", "created_at"]
        read_only_fields = ["score", "status", "created_at"]
