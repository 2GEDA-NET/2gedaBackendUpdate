from django.apps import AppConfig


class StereoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stereo'

    def ready(self):
        import stereo.signals
