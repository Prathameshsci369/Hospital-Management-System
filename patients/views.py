# patients/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from accounts.decorators import patient_required
from .models import PatientProfile
from doctors.models import DoctorProfile
from appointments.models import Appointment, AvailabilitySlot

@patient_required
def dashboard(request):
    patient = request.user.patient_profile
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        status='scheduled',
        availability_slot__date__gte=timezone.now().date()
    ).order_by('availability_slot__date', 'availability_slot__start_time')[:5]
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'patients/dashboard.html', context)

@patient_required
def doctors_list(request):
    doctors = DoctorProfile.objects.all()
    
    # Filter by specialization if provided
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)
    
    context = {
        'doctors': doctors,
        'specialization': specialization,
    }
    return render(request, 'patients/doctors_list.html', context)

@patient_required
def doctor_details(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    
    # Get available slots for this doctor
    available_slots = AvailabilitySlot.objects.filter(
        doctor=doctor,
        is_booked=False,
        date__gte=timezone.now().date()
    ).order_by('date', 'start_time')
    
    context = {
        'doctor': doctor,
        'available_slots': available_slots,
    }
    return render(request, 'patients/doctor_details.html', context)