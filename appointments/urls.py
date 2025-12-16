# appointments/urls.py
from django.urls import path
from . import views

app_name = 'appointments'  # This sets the namespace

urlpatterns = [
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('confirmation/<int:appointment_id>/', views.appointment_confirmation, name='appointment_confirmation'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
]