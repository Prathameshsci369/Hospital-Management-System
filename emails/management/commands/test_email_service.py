"""
Django management command to test the serverless email service
Usage: python manage.py test_email_service
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from emails.client import (
    send_welcome_email,
    send_appointment_confirmation,
    send_doctor_appointment_notification,
)
from appointments.models import Appointment
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test the serverless email service'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email-type',
            type=str,
            default='welcome',
            help='Type of email to send: welcome, appointment, doctor',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to send email to',
        )
        parser.add_argument(
            '--appointment-id',
            type=int,
            help='Appointment ID to send email for',
        )

    def handle(self, *args, **options):
        email_type = options.get('email_type', 'welcome')
        
        self.stdout.write(self.style.SUCCESS('Testing Serverless Email Service'))
        self.stdout.write('-' * 60)

        try:
            if email_type == 'welcome':
                self.test_welcome_email(options)
            elif email_type == 'appointment':
                self.test_appointment_email(options)
            elif email_type == 'doctor':
                self.test_doctor_email(options)
            else:
                raise CommandError(f"Unknown email type: {email_type}")

            self.stdout.write(self.style.SUCCESS('\n✓ Email test completed'))

        except Exception as e:
            raise CommandError(f'Error testing email: {str(e)}')

    def test_welcome_email(self, options):
        """Test welcome email."""
        self.stdout.write('\nTest: Welcome Email')
        self.stdout.write('-' * 60)

        user_id = options.get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise CommandError(f"User with ID {user_id} not found")
        else:
            # Get first user or create one
            user = User.objects.filter(is_staff=False).first()
            if not user:
                raise CommandError("No test user found. Create a user first.")

        self.stdout.write(f"User: {user.username} ({user.email})")
        self.stdout.write(f"Role: {user.role}")

        result = send_welcome_email(user)

        if result.get('success'):
            self.stdout.write(
                self.style.SUCCESS(f"✓ Email sent successfully")
            )
            self.stdout.write(f"  Message ID: {result.get('message_id')}")
            self.stdout.write(f"  Request ID: {result.get('request_id')}")
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Email failed to send")
            )
            self.stdout.write(f"  Error: {result.get('error')}")

    def test_appointment_email(self, options):
        """Test appointment confirmation email."""
        self.stdout.write('\nTest: Appointment Confirmation Email')
        self.stdout.write('-' * 60)

        appointment_id = options.get('appointment_id')
        
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id)
            except Appointment.DoesNotExist:
                raise CommandError(f"Appointment with ID {appointment_id} not found")
        else:
            # Get first appointment
            appointment = Appointment.objects.filter(status='scheduled').first()
            if not appointment:
                raise CommandError("No appointments found. Create an appointment first.")

        self.stdout.write(f"Patient: {appointment.patient.user.get_full_name() or appointment.patient.user.username}")
        self.stdout.write(f"Patient Email: {appointment.patient.user.email}")
        self.stdout.write(f"Doctor: Dr. {appointment.doctor.user.get_full_name()}")
        self.stdout.write(f"Date: {appointment.availability_slot.date}")
        self.stdout.write(f"Time: {appointment.availability_slot.start_time}")

        result = send_appointment_confirmation(appointment)

        if result.get('success'):
            self.stdout.write(
                self.style.SUCCESS(f"✓ Confirmation email sent successfully")
            )
            self.stdout.write(f"  Message ID: {result.get('message_id')}")
            self.stdout.write(f"  Request ID: {result.get('request_id')}")
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Email failed to send")
            )
            self.stdout.write(f"  Error: {result.get('error')}")

    def test_doctor_email(self, options):
        """Test doctor notification email."""
        self.stdout.write('\nTest: Doctor Appointment Notification Email')
        self.stdout.write('-' * 60)

        appointment_id = options.get('appointment_id')
        
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id)
            except Appointment.DoesNotExist:
                raise CommandError(f"Appointment with ID {appointment_id} not found")
        else:
            # Get first appointment
            appointment = Appointment.objects.filter(status='scheduled').first()
            if not appointment:
                raise CommandError("No appointments found. Create an appointment first.")

        self.stdout.write(f"Doctor: Dr. {appointment.doctor.user.get_full_name()}")
        self.stdout.write(f"Doctor Email: {appointment.doctor.user.email}")
        self.stdout.write(f"Patient: {appointment.patient.user.get_full_name() or appointment.patient.user.username}")
        self.stdout.write(f"Date: {appointment.availability_slot.date}")
        self.stdout.write(f"Time: {appointment.availability_slot.start_time}")

        result = send_doctor_appointment_notification(appointment)

        if result.get('success'):
            self.stdout.write(
                self.style.SUCCESS(f"✓ Notification email sent successfully")
            )
            self.stdout.write(f"  Message ID: {result.get('message_id')}")
            self.stdout.write(f"  Request ID: {result.get('request_id')}")
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Email failed to send")
            )
            self.stdout.write(f"  Error: {result.get('error')}")
