# patients/urls.py
from django.urls import path
from . import views

app_name = 'patients'  # This sets the namespace

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/<int:doctor_id>/', views.doctor_details, name='doctor_details'),
]