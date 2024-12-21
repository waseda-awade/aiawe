import logging

from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db.utils import ProgrammingError

logger = logging.getLogger(__name__)


class LlmCallerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "awe_system_ui.llm_caller"
    verbose_name = "LLM Caller"

    def ready(self):
        try:
            from .models import QuotaConfig

            QuotaConfig.get_default_quota()
        except (OperationalError, ProgrammingError):
            # Handle any exceptions that might occur during startup
            # such as database not being ready yet
            logging.exception("Error initializing LLM Caller app.")
