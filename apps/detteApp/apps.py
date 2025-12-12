from django.apps import AppConfig


class DetteAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.detteApp'

    def ready(self):
        # import signals to ensure post_save handlers are registered
        try:
            from . import signals  # noqa: F401
        except Exception:
            # don't break startup if signals fail; errors will show in logs
            pass
