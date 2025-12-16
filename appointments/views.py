# appointments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from accounts.decorators import patient_required
from .models import Appointment, AvailabilitySlot
from patients.models import PatientProfile
from google_integration.views import create_calendar_event  # <-- 1. ADD THIS IMPORT
from hospital_system.email_utils import send_booking_confirmation_email 
@patient_required
def book_appointment(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id)
    
    if slot.is_booked:
        messages.error(request, 'This slot is already booked.')
        return redirect('patients:doctor_details', doctor_id=slot.doctor.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        notes = request.POST.get('notes')
        
        patient = request.user.patient_profile
        
        # Use a transaction to prevent race conditions
        with transaction.atomic():
            # Lock the row for update
            slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
            
            if slot.is_booked:
                messages.error(request, 'This slot was just booked by someone else. Please try another slot.')
                return redirect('patients:doctor_details', doctor_id=slot.doctor.id)
            
            # Create the appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=slot.doctor,
                availability_slot=slot,
                reason=reason,
                notes=notes
            )
            
            # Mark the slot as booked
            slot.is_booked = True
            slot.save()
        send_booking_confirmation_email(appointment)  
        # Call the function to create Google Calendar events
        create_calendar_event(appointment)  # <-- 2. ADD THIS LINE
        
        messages.success(request, 'Appointment booked successfully.')
        return redirect('appointments:appointment_confirmation', appointment_id=appointment.id)
    
    context = {
        'slot': slot,
        'doctor': slot.doctor,
    }
    return render(request, 'appointments/book_appointment.html', context)

# ... (rest of the file remains the same)

@patient_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient_profile)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_confirmation.html', context)

@patient_required
def my_appointments(request):
    patient = request.user.patient_profile
    appointments = Appointment.objects.filter(patient=patient).order_by('-availability_slot__date', '-availability_slot__start_time')
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'appointments/my_appointments.html', context)