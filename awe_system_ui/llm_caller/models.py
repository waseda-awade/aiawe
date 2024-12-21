from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class QuotaConfig(models.Model):
    daily_limit = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "created_at"

    def __str__(self):
        return f"QuotaConfig(daily_limit={self.daily_limit})"

    @classmethod
    def get_default_quota(cls):
        try:
            # First try to get the latest quota config
            return cls.objects.latest()
        except cls.DoesNotExist:
            # If no quota exists, create a default one
            return cls.objects.create(daily_limit=10)


class APIRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    result = models.TextField(blank=True)
    error = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ],
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"APIRequest(user={self.user}, status={self.status}, \
            prompt={self.prompt[:20]})"
