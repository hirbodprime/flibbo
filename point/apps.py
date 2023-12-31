from django.apps import AppConfig


class PointConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'point'
    def ready(self):
        from point import signals
