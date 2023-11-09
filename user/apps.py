from django.apps import AppConfig
# import user.signals


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    def ready(self):
        import user.signals

default_app_config = 'user.apps.UserConfig'