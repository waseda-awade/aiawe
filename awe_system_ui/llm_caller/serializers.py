from rest_framework import serializers

from .models import APIRequest


class APIRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequest
        fields = ["id", "essay", "result", "error", "status", "created_at"]
        read_only_fields = ["result", "status", "created_at"]
