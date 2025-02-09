from django.apps import AppConfig


class LlmCallerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "awe_system_ui.llm_caller"
    verbose_name = "LLM Caller"

    def ready(self) -> None:
        import awe_system_ui.llm_caller.signals  # noqa: F401
