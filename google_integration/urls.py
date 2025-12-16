# google_integration/urls.py
from django.urls import path
from . import views

app_name = 'google_integration'

urlpatterns = [
    path('authorize/', views.authorize_calendar, name='authorize_calendar'),
    path('calendar/callback/', views.oauth2_callback, name='oauth2_callback'),
]