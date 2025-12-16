# doctors/urls.py
from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('availability/', views.manage_availability, name='manage_availability'),  # Changed from 'availability' to 'manage_availability'
    path('availability/add/', views.add_availability, name='add_availability'),
    path('availability/edit/<int:slot_id>/', views.edit_availability, name='edit_availability'),
    path('availability/delete/<int:slot_id>/', views.delete_availability, name='delete_availability'),
    path('appointments/', views.appointments, name='appointments'),
]