from django.apps import AppConfig
# import core.signals


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        import core.signals

default_app_config = 'core.apps.UserConfig'