"""
Django integration for serverless email service.
Provides simple API to send emails from Django views/signals.
"""

import json
import hashlib
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests

from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from emails.models import EmailSendLog
import uuid

# Add parent directory to path for serverless_email imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

logger = logging.getLogger(__name__)


class ServerlessEmailClient:
    """Client for sending emails via the serverless email service."""

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize email client.
        
        Args:
            api_url: URL of the API Gateway endpoint (defaults to settings)
            api_key: API key for authentication (defaults to settings)
        """
        self.api_url = api_url or getattr(
            settings,
            "SERVERLESS_EMAIL_API_URL",
            "http://localhost:3000/email/send",
        )
        self.api_key = api_key or getattr(
            settings,
            "SERVERLESS_EMAIL_API_KEY",
            "test-api-key-001",
        )
        self.use_local = getattr(settings, "SERVERLESS_EMAIL_USE_LOCAL", False)

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        template_name: str = None,
        template_vars: Dict[str, Any] = None,
        html_body: str = None,
        text_body: str = None,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[Dict] = None,
        tags: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            template_name: Name of email template to use
            template_vars: Variables to render in template
            html_body: HTML body (if not using template)
            text_body: Plain text body
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachment dicts
            tags: Custom tags for tracking
            
        Returns:
            Dict with send result
        """
        request_id = str(uuid.uuid4())

        # Use local emulator if configured
        if self.use_local:
            return self._send_locally(
                request_id,
                to_addresses,
                subject,
                template_name,
                template_vars,
                html_body,
                text_body,
                cc,
                bcc,
                attachments,
                tags,
            )

        # Build request payload
        payload = {
            "request_id": request_id,
            "to": to_addresses,
            "subject": subject,
        }

        if template_name:
            payload["template"] = template_name
            payload["variables"] = template_vars or {}
        else:
            if html_body:
                payload["html"] = html_body
            if text_body:
                payload["text"] = text_body

        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc
        if attachments:
            payload["attachments"] = attachments
        if tags:
            payload["tags"] = tags

        # Log the request
        log_entry = EmailSendLog.objects.create(
            request_id=request_id,
            from_address=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            to_addresses=to_addresses,
            cc_addresses=cc or [],
            bcc_addresses=bcc or [],
            subject=subject,
            template_used=template_name,
            template_variables=template_vars or {},
            tags=tags or {},
        )

        # Send via API
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                log_entry.mark_sent(result.get("message_id", "unknown"))
                return {
                    "success": True,
                    "request_id": request_id,
                    "message_id": result.get("message_id"),
                }
            else:
                error_msg = response.text
                log_entry.mark_failed("API_ERROR", error_msg, retryable=True)
                return {
                    "success": False,
                    "request_id": request_id,
                    "error": error_msg,
                    "status_code": response.status_code,
                }
        except requests.RequestException as e:
            logger.error(f"Failed to send email via API: {str(e)}")
            log_entry.mark_failed("CONNECTION_ERROR", str(e), retryable=True)
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e),
            }

    def _send_locally(
        self,
        request_id: str,
        to_addresses: List[str],
        subject: str,
        template_name: str,
        template_vars: Dict[str, Any],
        html_body: str,
        text_body: str,
        cc: List[str],
        bcc: List[str],
        attachments: List[Dict],
        tags: Dict[str, str],
    ) -> Dict[str, Any]:
        """Send using local emulator."""
        from serverless_email.local_emulator import get_local_emulator

        emulator = get_local_emulator()

        # Log the request
        log_entry = EmailSendLog.objects.create(
            request_id=request_id,
            from_address=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            to_addresses=to_addresses,
            cc_addresses=cc or [],
            bcc_addresses=bcc or [],
            subject=subject,
            template_used=template_name,
            template_variables=template_vars or {},
            tags=tags or {},
        )

        result = emulator.send_email(
            to_addresses=to_addresses,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            template_name=template_name,
            template_vars=template_vars,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
        )

        if result["success"]:
            log_entry.mark_sent(result["message_id"])
            return {
                "success": True,
                "request_id": request_id,
                "message_id": result["message_id"],
            }
        else:
            log_entry.mark_failed("SEND_ERROR", result.get("error", "Unknown error"))
            return {
                "success": False,
                "request_id": request_id,
                "error": result.get("error"),
            }

    def send_appointment_confirmation(self, appointment) -> Dict[str, Any]:
        """Send appointment confirmation email to patient."""
        from patients.models import PatientProfile

        patient = appointment.patient
        doctor = appointment.doctor
        slot = appointment.availability_slot

        return self.send_email(
            to_addresses=[patient.user.email],
            subject="Appointment Confirmation",
            template_name="appointment_confirmation",
            template_vars={
                "patient_name": patient.user.first_name or "Patient",
                "doctor_name": f"Dr. {doctor.user.first_name} {doctor.user.last_name}",
                "specialization": doctor.specialization,
                "date": slot.date.strftime("%B %d, %Y"),
                "time": slot.start_time.strftime("%I:%M %p"),
                "reason": appointment.reason[:100],
                "appointment_link": getattr(settings, "APPOINTMENT_VIEW_URL", "#"),
                "hospital_name": getattr(settings, "HOSPITAL_NAME", "Hospital Management System"),
            },
            tags={
                "email_type": "appointment_confirmation",
                "appointment_id": str(appointment.id),
                "patient_id": str(patient.id),
            },
        )

    def send_appointment_reminder(self, appointment) -> Dict[str, Any]:
        """Send appointment reminder email to patient."""
        patient = appointment.patient
        doctor = appointment.doctor
        slot = appointment.availability_slot

        return self.send_email(
            to_addresses=[patient.user.email],
            subject="Appointment Reminder",
            template_name="appointment_reminder",
            template_vars={
                "patient_name": patient.user.first_name or "Patient",
                "doctor_name": f"Dr. {doctor.user.first_name} {doctor.user.last_name}",
                "date": slot.date.strftime("%B %d, %Y"),
                "time": slot.start_time.strftime("%I:%M %p"),
            },
            tags={
                "email_type": "appointment_reminder",
                "appointment_id": str(appointment.id),
            },
        )

    def send_welcome_email(self, user) -> Dict[str, Any]:
        """Send welcome email to new user."""
        role = getattr(user, "role", "patient")
        return self.send_email(
            to_addresses=[user.email],
            subject="Welcome to Hospital Management System",
            template_name="welcome",
            template_vars={
                "user_name": user.first_name or user.username,
                "role": "Doctor" if role == "doctor" else "Patient",
                "login_link": getattr(settings, "LOGIN_URL", "http://localhost:8000/login"),
            },
            tags={
                "email_type": "welcome",
                "user_id": str(user.id),
                "user_role": role,
            },
        )

    def send_doctor_appointment_notification(self, appointment) -> Dict[str, Any]:
        """Send new appointment notification to doctor."""
        doctor = appointment.doctor
        patient = appointment.patient
        slot = appointment.availability_slot

        return self.send_email(
            to_addresses=[doctor.user.email],
            subject="New Appointment Scheduled",
            template_name="doctor_new_appointment",
            template_vars={
                "doctor_name": f"Dr. {doctor.user.first_name} {doctor.user.last_name}",
                "patient_name": patient.user.first_name or "Patient",
                "date": slot.date.strftime("%B %d, %Y"),
                "time": slot.start_time.strftime("%I:%M %p"),
                "reason": appointment.reason[:100],
            },
            tags={
                "email_type": "doctor_new_appointment",
                "appointment_id": str(appointment.id),
                "doctor_id": str(doctor.id),
            },
        )


def get_email_client() -> ServerlessEmailClient:
    """Get or create the email client instance."""
    return ServerlessEmailClient()


def send_appointment_confirmation(appointment) -> Dict[str, Any]:
    """Convenience function to send appointment confirmation."""
    client = get_email_client()
    return client.send_appointment_confirmation(appointment)


def send_appointment_reminder(appointment) -> Dict[str, Any]:
    """Convenience function to send appointment reminder."""
    client = get_email_client()
    return client.send_appointment_reminder(appointment)


def send_welcome_email(user) -> Dict[str, Any]:
    """Convenience function to send welcome email."""
    client = get_email_client()
    return client.send_welcome_email(user)


def send_doctor_appointment_notification(appointment) -> Dict[str, Any]:
    """Convenience function to send doctor notification."""
    client = get_email_client()
    return client.send_doctor_appointment_notification(appointment)
