from django.db import models

# Create your models here.
# patients/models.py
from django.db import models
from accounts.models import User

# patients/models.py
from django.db import models
from accounts.models import User

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    medical_history = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"