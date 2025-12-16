# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import DoctorSignUpForm, PatientSignUpForm, LoginForm

def signup_view(request):
    return render(request, 'accounts/signup.html')

def doctor_signup_view(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create DoctorProfile
            from doctors.models import DoctorProfile
            DoctorProfile.objects.create(user=user)
            
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('doctors:dashboard')
    else:
        form = DoctorSignUpForm()
    return render(request, 'accounts/doctor_signup.html', {'form': form})

def patient_signup_view(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create PatientProfile
            from patients.models import PatientProfile
            PatientProfile.objects.create(user=user)
            
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('patients:dashboard')
    else:
        form = PatientSignUpForm()
    return render(request, 'accounts/patient_signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user role
                if user.is_doctor():
                    return redirect('doctors:dashboard')
                elif user.is_patient():
                    return redirect('patients:dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile(request):
    user = request.user
    if user.is_doctor():
        try:
            profile = user.doctor_profile
            context = {
                'user': user,
                'profile': profile,
                'role': 'Doctor'
            }
        except:
            context = {
                'user': user,
                'role': 'Doctor',
                'error': 'Profile not found'
            }
    elif user.is_patient():
        try:
            profile = user.patient_profile
            context = {
                'user': user,
                'profile': profile,
                'role': 'Patient'
            }
        except:
            context = {
                'user': user,
                'role': 'Patient',
                'error': 'Profile not found'
            }
    else:
        context = {
            'user': user,
            'role': 'Unknown'
        }
    
    return render(request, 'accounts/profile.html', context)