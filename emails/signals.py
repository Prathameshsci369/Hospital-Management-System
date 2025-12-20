"""
Django signals for email service
Automatically sends emails on events (user registration, appointment creation, etc.)
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from appointments.models import Appointment

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def send_welcome_on_user_creation(sender, instance, created, **kwargs):
    """Send welcome email when user account is created."""
    if created:
        try:
            from emails.client import send_welcome_email
            result = send_welcome_email(instance)
            if result.get("success"):
                logger.info(f"Welcome email sent to {instance.email}")
            else:
                logger.warning(f"Failed to send welcome email: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}", exc_info=True)


@receiver(post_save, sender=Appointment)
def send_appointment_emails(sender, instance, created, **kwargs):
    """Send appointment emails when appointment is created."""
    if created:
        try:
            from emails.client import (
                send_appointment_confirmation,
                send_doctor_appointment_notification,
            )
            
            logger.info(f"Sending appointment emails for appointment {instance.id}")
            
            # Send confirmation to patient
            patient_result = send_appointment_confirmation(instance)
            if patient_result.get("success"):
                logger.info(f"Patient confirmation email sent: {patient_result.get('message_id')}")
            else:
                logger.warning(f"Failed to send patient confirmation: {patient_result.get('error')}")
            
            # Send notification to doctor
            doctor_result = send_doctor_appointment_notification(instance)
            if doctor_result.get("success"):
                logger.info(f"Doctor notification email sent: {doctor_result.get('message_id')}")
            else:
                logger.warning(f"Failed to send doctor notification: {doctor_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending appointment emails: {str(e)}", exc_info=True)
