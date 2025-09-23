from django.apps import AppConfig


class DjangoXrechnungConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_xrechnung"
    verbose_name = "Django XRechnung"
    
    def ready(self):
        """
        Perform initialization tasks when Django starts.
        This method is called when the app is ready.
        """
        # Import signal handlers or perform other initialization
        pass