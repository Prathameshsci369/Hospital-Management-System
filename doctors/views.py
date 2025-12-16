# doctors/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from accounts.decorators import doctor_required
from .models import DoctorProfile
from appointments.models import Appointment, AvailabilitySlot

@doctor_required
def dashboard(request):
    doctor = request.user.doctor_profile
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='scheduled',
        availability_slot__date__gte=timezone.now().date()
    ).order_by('availability_slot__date', 'availability_slot__start_time')[:5]
    
    context = {
        'doctor': doctor,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'doctors/dashboard.html', context)

@doctor_required
def manage_availability(request):
    doctor = request.user.doctor_profile
    availability_slots = AvailabilitySlot.objects.filter(doctor=doctor).order_by('date', 'start_time')
    
    context = {
        'availability_slots': availability_slots,
    }
    return render(request, 'doctors/manage_availability.html', context)

@doctor_required
def add_availability(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        doctor = request.user.doctor_profile
        
        # Check if the slot overlaps with existing slots
        if AvailabilitySlot.check_overlap(doctor, date, start_time, end_time):
            messages.error(request, 'This time slot overlaps with an existing slot.')
            return redirect('doctors:add_availability')
        
        # Check if the date is in the future
        if timezone.datetime.strptime(date, '%Y-%m-%d').date() < timezone.now().date():
            messages.error(request, 'You cannot add availability for past dates.')
            return redirect('doctors:add_availability')
        
        # Create the availability slot
        AvailabilitySlot.objects.create(
            doctor=doctor,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        
        messages.success(request, 'Availability slot added successfully.')
        return redirect('doctors:manage_availability')
    
    return render(request, 'doctors/add_availability.html')

@doctor_required
def edit_availability(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id, doctor=request.user.doctor_profile)
    
    if slot.is_booked:
        messages.error(request, 'Cannot edit a booked slot.')
        return redirect('doctors:manage_availability')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        # Check if the slot overlaps with existing slots (excluding the current slot)
        if AvailabilitySlot.check_overlap(slot.doctor, date, start_time, end_time, exclude_id=slot.id):
            messages.error(request, 'This time slot overlaps with an existing slot.')
            return redirect('doctors:edit_availability', slot_id=slot.id)
        
        # Check if the date is in the future
        if timezone.datetime.strptime(date, '%Y-%m-%d').date() < timezone.now().date():
            messages.error(request, 'You cannot set availability for past dates.')
            return redirect('doctors:edit_availability', slot_id=slot.id)
        
        # Update the availability slot
        slot.date = date
        slot.start_time = start_time
        slot.end_time = end_time
        slot.save()
        
        messages.success(request, 'Availability slot updated successfully.')
        return redirect('doctors:manage_availability')
    
    context = {
        'slot': slot,
    }
    return render(request, 'doctors/edit_availability.html', context)

@doctor_required
def delete_availability(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id, doctor=request.user.doctor_profile)
    
    if slot.is_booked:
        messages.error(request, 'Cannot delete a booked slot.')
    else:
        slot.delete()
        messages.success(request, 'Availability slot deleted successfully.')
    
    return redirect('doctors:manage_availability')

@doctor_required
def appointments(request):
    doctor = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-availability_slot__date', '-availability_slot__start_time')
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'doctors/appointments.html', context)