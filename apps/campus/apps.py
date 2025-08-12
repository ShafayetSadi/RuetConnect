from django.apps import AppConfig


class CampusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.campus"

    def ready(self):
        # Ensure signals are registered
        from . import signals  # noqa: F401
