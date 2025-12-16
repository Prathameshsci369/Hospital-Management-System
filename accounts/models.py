from django.db import models
# accounts/models.py
from django.contrib.auth.models import AbstractUser



    

# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    DOCTOR = 'doctor'
    PATIENT = 'patient'
    
    ROLE_CHOICES = (
        (DOCTOR, 'Doctor'),
        (PATIENT, 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PATIENT)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_doctor(self):
        return self.role == self.DOCTOR
    
    def is_patient(self):
        return self.role == self.PATIENT