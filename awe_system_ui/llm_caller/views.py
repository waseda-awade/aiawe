from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import APIRequest
from .models import QuotaConfig
from .serializers import APIRequestSerializer
from .tasks import process_openai_request


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class APIRequestViewSet(viewsets.ModelViewSet):
    serializer_class = APIRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = APIRequest.objects.filter(user=self.request.user)
        # Add ordering to ensure consistent pagination
        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        # Check quota
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        today_start = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time()),
        )
        today_end = timezone.make_aware(
            timezone.datetime.combine(tomorrow, timezone.datetime.min.time()),
        )

        # Get current quota config, creating default if none exists
        quota_config = QuotaConfig.get_default_quota()

        # Count today's requests
        today_requests = APIRequest.objects.filter(
            user=request.user,
            created_at__range=(today_start, today_end),
        ).count()

        if today_requests >= quota_config.daily_limit:
            return Response(
                {"error": "Daily quota exceeded"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Create request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_request = serializer.save(user=request.user)

        # Start async task
        task = process_openai_request.delay(api_request.id)
        api_request.task_id = task.id
        api_request.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
