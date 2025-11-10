from django.apps import AppConfig


class AppConfig(AppConfig):
    """
    Configuration class for the 'app' Django application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'Agile Budget Tracker'
    
    def ready(self):
        """
        Method called when Django starts.
        Use this to register signals or perform other initialization.
        """
        # Import signals here if you have any
        # Example: import app.signals
        pass