# google_integration/models.py
from django.db import models
from django.conf import settings
from accounts.models import User
from google.oauth2.credentials import Credentials

class GoogleCalendarToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_calendar_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()
    
    def __str__(self):
        return f"Calendar token for {self.user.username}"
    
    def to_google_credentials(self):
        return Credentials(
            token=self.access_token,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/calendar']
        )