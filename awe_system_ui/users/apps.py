import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "awe_system_ui.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import awe_system_ui.users.signals  # noqa: F401
