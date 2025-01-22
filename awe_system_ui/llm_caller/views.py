from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import APIRequest
from .models import LLMConfig
from .models import LLMModel
from .models import QuotaConfig
from .serializers import APIRequestSerializer
from .serializers import LLMModelSerializer
from .tasks import process_openai_request
from .utils import get_today_date_range


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
        # Create request first to validate the model
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the model instance
        model_name = serializer.validated_data["model_name"]
        model = LLMModel.objects.filter(name=model_name, is_active=True).first()
        if not model:
            return Response(
                {"model_name": f"Model not found: {model_name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check quota for this specific model
        today_start, today_end = get_today_date_range()

        # Get quota config for this model - if it doesn't exist, treat as unlimited
        try:
            quota_config = QuotaConfig.objects.get(model=model)

            # Count today's requests for this model
            today_requests = APIRequest.objects.filter(
                user=request.user,
                model=model,
                created_at__range=(today_start, today_end),
            ).count()

            if today_requests >= quota_config.daily_limit:
                return Response(
                    {"error": f"Daily quota exceeded for model {model.display_name}"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
        except QuotaConfig.DoesNotExist:
            # No quota config means unlimited requests
            pass

        # Create and save the request first
        api_request = serializer.save(user=request.user)
        api_request.save()  # Ensure it's saved to the database

        # Start async task
        task = process_openai_request.delay(
            api_request.id,
            api_request.model.name,
            LLMConfig.get_active_config().temperature,
            LLMConfig.get_active_config().system_prompt,
            LLMConfig.get_active_config().user_prompt_template,
        )

        # Update task_id in a separate transaction
        api_request.task_id = task.id
        api_request.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ActiveModelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_models = LLMModel.get_active_models()
        serializer = LLMModelSerializer(
            active_models,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
