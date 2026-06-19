from dataclasses import asdict

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import APIRequest
from .models import LLMConfig
from .models import LLMModel
from .serializers import APIRequestSerializer
from .serializers import LLMModelSerializer
from .tasks import LLMRequestParams
from .tasks import process_openai_request
from .turnstile import verify_turnstile


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class APIRequestViewSet(viewsets.ModelViewSet):
    serializer_class = APIRequestSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # Allow anonymous users to poll their own submitted request by ID;
            # list/other actions still return empty via the standard pagination.
            if self.action == "retrieve":
                return APIRequest.objects.filter(
                    created_by__isnull=True,
                    is_deleted=False,
                )
            return APIRequest.objects.none()
        queryset = APIRequest.objects.filter(
            created_by=self.request.user,
            is_deleted=False,
        )
        return queryset.order_by("-created_at")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Create request first to validate the model
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the model instance
        model_id = serializer.validated_data["model_id"]
        model = LLMModel.objects.filter(id=model_id, is_active=True).first()
        if not model:
            return Response(
                {"model_id": f"Model not found: {model_id}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_authenticated:
            # Check quota
            if not model.check_quota(request.user):
                msg = f"Daily quota exceeded for model {model.display_name}"
                return Response(
                    {"model_id": msg},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            api_request = serializer.save(created_by=request.user)
        else:
            # Verify Turnstile challenge
            token = request.data.get("turnstile_token")
            if not token or not verify_turnstile(
                token, request.META.get("REMOTE_ADDR")
            ):
                return Response(
                    {"detail": "Turnstile verification failed."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            # Require model to allow anonymous access
            if not model.available_to_anonymous:
                return Response(
                    {"model_id": "This model requires an account."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            # No quota check for anonymous; row saved with created_by=None
            api_request = serializer.save(created_by=None)

        llm_config = LLMConfig.get_active_config(model_name=model.name)
        llm_params = LLMRequestParams(
            request_id=api_request.id,
            model_name=model.name,
            temperature=llm_config.temperature,
            system_prompt=llm_config.system_prompt,
            user_prompt_template=llm_config.user_prompt_template,
            feedback_language=api_request.feedback_language,
        )

        # Ensure the actual task execution happens after transaction commit
        transaction.on_commit(
            lambda: process_openai_request.delay(
                asdict(llm_params),
                delay_seconds=getattr(settings, "TASK_DELAY", 0),
            ),
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "No IDs provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update is_deleted flag for user's requests
        updated = APIRequest.objects.filter(
            id__in=ids,
            created_by=request.user,
            is_deleted=False,
        ).update(is_deleted=True)

        return Response({"deleted_count": updated})


class ActiveModelsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            active_models = LLMModel.get_active_models()
        else:
            active_models = LLMModel.get_active_models().filter(
                available_to_anonymous=True,
            )
        serializer = LLMModelSerializer(
            active_models,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
