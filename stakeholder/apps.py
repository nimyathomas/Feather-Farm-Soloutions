from django.apps import AppConfig

class StakeholderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stakeholder'

    def ready(self):
        # Remove any TensorFlow-related initialization
        pass
