"""
Django models for email tracking and logging.
Stores email send history, delivery status, and bounce/complaint information.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailTemplate(models.Model):
    """Stores custom email templates."""

    TEMPLATE_CHOICES = (
        ("appointment_confirmation", "Appointment Confirmation"),
        ("appointment_reminder", "Appointment Reminder"),
        ("appointment_cancelled", "Appointment Cancelled"),
        ("welcome", "Welcome Email"),
        ("doctor_new_appointment", "Doctor New Appointment"),
        ("custom", "Custom Template"),
    )

    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_CHOICES)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    variables_required = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["template_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.template_type})"


class EmailSendLog(models.Model):
    """Tracks all email send attempts."""

    STATUS_CHOICES = (
        ("sent", "Sent"),
        ("bounced", "Bounced"),
        ("complained", "Complained"),
        ("delivery_delayed", "Delivery Delayed"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    )

    # Request tracking
    request_id = models.CharField(max_length=100, unique=True, db_index=True)
    message_id = models.CharField(max_length=255, blank=True, db_index=True)

    # Email details
    from_address = models.EmailField()
    to_addresses = models.JSONField()  # List of recipient emails
    cc_addresses = models.JSONField(default=list, blank=True)
    bcc_addresses = models.JSONField(default=list, blank=True)
    subject = models.CharField(max_length=200)

    # Template info
    template_used = models.CharField(max_length=100, blank=True)
    template_variables = models.JSONField(default=dict, blank=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    is_retryable = models.BooleanField(default=False)

    # Attachment tracking
    attachment_count = models.PositiveIntegerField(default=0)
    total_attachment_size = models.PositiveIntegerField(default=0)  # In bytes

    # Metadata
    source_ip = models.GenericIPAddressField(blank=True, null=True)
    api_key_hash = models.CharField(max_length=64, blank=True)  # Hashed for security
    tags = models.JSONField(default=dict, blank=True)  # Custom tags for filtering

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["from_address", "created_at"]),
            models.Index(fields=["message_id"]),
        ]

    def __str__(self):
        return f"{self.request_id} - {self.subject}"

    def mark_sent(self, message_id: str) -> None:
        """Mark email as sent."""
        self.status = "sent"
        self.message_id = message_id
        self.sent_at = timezone.now()
        self.save()

    def mark_delivered(self) -> None:
        """Mark email as delivered."""
        self.status = "sent"  # SES treats delivery as sent
        self.delivered_at = timezone.now()
        self.save()

    def mark_bounced(self, error_message: str = None) -> None:
        """Mark email as bounced."""
        self.status = "bounced"
        if error_message:
            self.error_message = error_message
        self.save()

    def mark_complained(self) -> None:
        """Mark email as complained."""
        self.status = "complained"
        self.save()

    def mark_failed(self, error_code: str, error_message: str, retryable: bool = False) -> None:
        """Mark email as failed."""
        self.status = "failed"
        self.error_code = error_code
        self.error_message = error_message
        self.is_retryable = retryable
        self.save()

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
        self.save()

    @property
    def recipient_count(self) -> int:
        """Get total recipient count."""
        count = len(self.to_addresses) if self.to_addresses else 0
        count += len(self.cc_addresses) if self.cc_addresses else 0
        count += len(self.bcc_addresses) if self.bcc_addresses else 0
        return count

    @property
    def can_retry(self) -> bool:
        """Check if email can be retried."""
        return self.is_retryable and self.retry_count < 3


class EmailRateLimit(models.Model):
    """Tracks rate limiting per API key and source IP."""

    IDENTIFIER_TYPE_CHOICES = (
        ("api_key", "API Key"),
        ("ip_address", "IP Address"),
    )

    identifier_type = models.CharField(max_length=20, choices=IDENTIFIER_TYPE_CHOICES)
    identifier_value = models.CharField(max_length=255, db_index=True)
    identifier_hash = models.CharField(max_length=64, unique=True, db_index=True)  # For privacy

    emails_sent_current_hour = models.PositiveIntegerField(default=0)
    emails_sent_current_day = models.PositiveIntegerField(default=0)
    emails_sent_total = models.PositiveIntegerField(default=0)

    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=255, blank=True)
    block_until = models.DateTimeField(null=True, blank=True)

    last_request_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = [["identifier_type", "identifier_hash"]]

    def __str__(self):
        return f"{self.identifier_type}: {self.identifier_value[:50]}"

    @property
    def is_rate_limited(self) -> bool:
        """Check if this identifier is currently rate limited."""
        if self.is_blocked:
            if self.block_until and timezone.now() > self.block_until:
                self.is_blocked = False
                self.save()
                return False
            return True
        return False


class EmailAttachment(models.Model):
    """Tracks email attachments."""

    email_log = models.ForeignKey(
        EmailSendLog,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()  # In bytes
    s3_url = models.URLField(blank=True)  # S3 URL for attachment storage
    upload_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("uploaded", "Uploaded"), ("failed", "Failed")],
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} ({self.size} bytes)"

    @property
    def size_mb(self) -> float:
        """Get size in MB."""
        return self.size / (1024 * 1024)


class EmailSESEvent(models.Model):
    """Tracks SES events (bounces, complaints, delivery)."""

    EVENT_TYPE_CHOICES = (
        ("send", "Send"),
        ("delivery", "Delivery"),
        ("open", "Open"),
        ("click", "Click"),
        ("bounce", "Bounce"),
        ("complaint", "Complaint"),
        ("delivery_delay", "Delivery Delay"),
        ("subscription", "Subscription"),
    )

    BOUNCE_TYPE_CHOICES = (
        ("permanent", "Permanent"),
        ("transient", "Transient"),
    )

    email_log = models.ForeignKey(
        EmailSendLog,
        on_delete=models.CASCADE,
        related_name="ses_events",
    )

    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, db_index=True)
    event_timestamp = models.DateTimeField(db_index=True)

    # SES event data
    ses_message_id = models.CharField(max_length=255, blank=True)
    bounce_type = models.CharField(
        max_length=20,
        choices=BOUNCE_TYPE_CHOICES,
        blank=True,
    )
    bounced_recipients = models.JSONField(default=list, blank=True)
    complained_recipients = models.JSONField(default=list, blank=True)
    bounce_subtype = models.CharField(max_length=100, blank=True)

    # Raw event data from SES
    raw_event_data = models.JSONField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_timestamp"]
        indexes = [
            models.Index(fields=["event_type", "event_timestamp"]),
            models.Index(fields=["email_log", "event_type"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.email_log.request_id}"
