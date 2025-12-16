# accounts/decorators.py
from django.shortcuts import redirect
from django.contrib import messages

def doctor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_doctor():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You need to be logged in as a doctor to access this page.')
            return redirect('accounts:login')
    return wrapper

def patient_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_patient():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You need to be logged in as a patient to access this page.')
            return redirect('accounts:login')
    return wrapper