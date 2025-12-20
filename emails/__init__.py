"""
Django email tracking and management app
"""

from django.apps import AppConfig


class EmailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emails'
    verbose_name = 'Email Service'

    def ready(self):
        # Import signals
        import emails.signals  # noqa
