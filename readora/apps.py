from django.apps import AppConfig

class ReadoraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Readora'

    def ready(self):
        import Readora.signals  # 👈 This line is critical
