# appointments/models.py
from django.db import models
from django.db.models import Q
from django.utils import timezone
from accounts.models import User
from doctors.models import DoctorProfile
from patients.models import PatientProfile

class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.doctor} - {self.date} ({self.start_time} to {self.end_time})"
    
    @classmethod
    def check_overlap(cls, doctor, date, start_time, end_time, exclude_id=None):
        """
        Check if the new slot overlaps with existing slots for the same doctor on the same day.
        """
        query = Q(doctor=doctor, date=date)
        
        # Check if the new slot starts during an existing slot
        query |= Q(doctor=doctor, date=date, start_time__lte=start_time, end_time__gt=start_time)
        
        # Check if the new slot ends during an existing slot
        query |= Q(doctor=doctor, date=date, start_time__lt=end_time, end_time__gte=end_time)
        
        # Check if the new slot completely contains an existing slot
        query |= Q(doctor=doctor, date=date, start_time__gte=start_time, end_time__lte=end_time)
        
        if exclude_id:
            query &= ~Q(id=exclude_id)
            
        return cls.objects.filter(query).exists()

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    availability_slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE, related_name='appointment')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.availability_slot.date}"