from django.apps import AppConfig


class FollowingSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'following_system'
    def ready(self):
        import following_system.signals