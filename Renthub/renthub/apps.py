from django.apps import AppConfig


class RenthubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "renthub"

    def ready(self):
        import renthub.signals