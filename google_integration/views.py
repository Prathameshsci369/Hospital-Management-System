# google_integration/views.py
import os
import datetime
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.utils import timezone  # <-- THIS IMPORT IS CRUCIAL
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from .models import GoogleCalendarToken

# Path to your credentials file
CREDENTIALS_FILE = os.path.join(settings.BASE_DIR, 'credentials.json')

# Scopes define the level of access you are requesting.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Hardcode the redirect URI to match what's in your Google Cloud Console
REDIRECT_URI = 'http://127.0.0.1:8000/accounts/google/calendar/callback/'

def authorize_calendar(request):
    # Set environment variable to allow insecure transport for local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    # Generate a URL for the authorization request.
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store the state in the session so we can verify it in the callback.
    request.session['oauth_state'] = state
    
    return redirect(authorization_url)

def oauth2_callback(request):
    # Set environment variable to allow insecure transport for local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # Verify the state to protect against CSRF attacks.
    state = request.session.get('oauth_state')
    if state is None or state != request.GET.get('state'):
        messages.error(request, 'Invalid state parameter. Authorization failed.')
        return redirect('home')

    # Create a flow instance to exchange the authorization code for an access token.
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    
    # Store the credentials in our database.
    credentials = flow.credentials
    token, _ = GoogleCalendarToken.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_expiry': timezone.now(),  # <-- This line now works because of the import
        }
    )
    
    messages.success(request, 'Successfully connected your Google Calendar!')
    return redirect('accounts:profile')

def create_calendar_event(appointment):
    """
    Creates an event in the Google Calendar for the given appointment.
    This function will be called from the appointments app after a successful booking.
    """
    print(f"DEBUG: create_calendar_event called for appointment {appointment.id}")  # <-- ADD THIS DEBUG LINE
    
    try:
        # Get the token for the doctor
        doctor_token = GoogleCalendarToken.objects.get(user=appointment.doctor.user)
        doctor_credentials = doctor_token.to_google_credentials()
        print(f"DEBUG: Retrieved doctor token for {appointment.doctor.user.username}")  # <-- ADD THIS DEBUG LINE
        
        # Get the token for the patient
        patient_token = GoogleCalendarToken.objects.get(user=appointment.patient.user)
        patient_credentials = patient_token.to_google_credentials()
        print(f"DEBUG: Retrieved patient token for {appointment.patient.user.username}")  # <-- ADD THIS DEBUG LINE
        
        # Build the service objects
        doctor_service = build('calendar', 'v3', credentials=doctor_credentials)
        patient_service = build('calendar', 'v3', credentials=patient_credentials)
        print(f"DEBUG: Built calendar services")  # <-- ADD THIS DEBUG LINE
        
        # Event details
        event_summary = f"Appointment with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}"
        event_description = f"Reason: {appointment.reason}"
        
        start_datetime = datetime.datetime.combine(
            appointment.availability_slot.date, 
            appointment.availability_slot.start_time
        )
        end_datetime = datetime.datetime.combine(
            appointment.availability_slot.date, 
            appointment.availability_slot.end_time
        )
        
        event = {
            'summary': event_summary,
            'description': event_description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'UTC', # Or use the user's timezone
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'UTC', # Or use the user's timezone
            },
        }
        
        print(f"DEBUG: Event data prepared: {event}")  # <-- ADD THIS DEBUG LINE
        
        # Create the event in the doctor's calendar
        doctor_event = doctor_service.events().insert(calendarId='primary', body=event).execute()
        print(f"DEBUG: Created event in doctor's calendar: {doctor_event.get('htmlLink')}")  # <-- ADD THIS DEBUG LINE
        
        # Create the event in the patient's calendar
        patient_event = patient_service.events().insert(calendarId='primary', body=event).execute()
        print(f"DEBUG: Created event in patient's calendar: {patient_event.get('htmlLink')}")  # <-- ADD THIS DEBUG LINE
        
        return True
    except GoogleCalendarToken.DoesNotExist:
        print(f"ERROR: GoogleCalendarToken.DoesNotExist for user {appointment.doctor.user.username} or {appointment.patient.user.username}")  # <-- ADD THIS DEBUG LINE
        return False
    except Exception as e:
        # Handle other potential errors (e.g., API errors)
        print(f"ERROR: An error occurred: {e}")  # <-- ENHANCE THIS DEBUG LINE
        return False