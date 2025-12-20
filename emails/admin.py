"""
Django admin interface for email service
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from emails.models import (
    EmailTemplate,
    EmailSendLog,
    EmailRateLimit,
    EmailAttachment,
    EmailSESEvent,
)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'created_at')
    list_filter = ('template_type', 'is_active', 'created_at')
    search_fields = ('name', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'subject', 'is_active')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content')
        }),
        ('Configuration', {
            'fields': ('variables_required',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class EmailAttachmentInline(admin.TabularInline):
    model = EmailAttachment
    extra = 0
    readonly_fields = ('filename', 'content_type', 'size_mb', 'created_at')
    fields = ('filename', 'content_type', 'size_mb', 'upload_status')


class EmailSESEventInline(admin.TabularInline):
    model = EmailSESEvent
    extra = 0
    readonly_fields = ('event_type', 'event_timestamp', 'created_at')
    fields = ('event_type', 'event_timestamp', 'bounce_type')


@admin.register(EmailSendLog)
class EmailSendLogAdmin(admin.ModelAdmin):
    list_display = (
        'request_id_short',
        'subject_short',
        'recipient_count',
        'status_badge',
        'sent_at_short',
    )
    list_filter = ('status', 'created_at', 'template_used')
    search_fields = ('request_id', 'subject', 'to_addresses')
    readonly_fields = (
        'request_id',
        'message_id',
        'created_at',
        'updated_at',
        'recipient_count',
        'size_mb_display',
    )
    inlines = (EmailAttachmentInline, EmailSESEventInline)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'message_id')
        }),
        ('Email Details', {
            'fields': ('from_address', 'to_addresses', 'cc_addresses', 'bcc_addresses', 'subject')
        }),
        ('Template & Variables', {
            'fields': ('template_used', 'template_variables'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'delivered_at')
        }),
        ('Error Information', {
            'fields': ('error_message', 'error_code', 'retry_count', 'is_retryable'),
            'classes': ('collapse',)
        }),
        ('Attachments', {
            'fields': ('attachment_count', 'size_mb_display'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('source_ip', 'api_key_hash', 'tags'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def request_id_short(self, obj):
        return obj.request_id[:8] + '...'
    request_id_short.short_description = 'Request ID'

    def subject_short(self, obj):
        return obj.subject[:50] + ('...' if len(obj.subject) > 50 else '')
    subject_short.short_description = 'Subject'

    def sent_at_short(self, obj):
        if obj.sent_at:
            return obj.sent_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    sent_at_short.short_description = 'Sent At'

    def status_badge(self, obj):
        colors = {
            'sent': 'green',
            'failed': 'red',
            'pending': 'orange',
            'bounced': 'red',
            'complained': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'

    def size_mb_display(self, obj):
        if obj.total_attachment_size:
            mb = obj.total_attachment_size / (1024 * 1024)
            return f"{mb:.2f} MB"
        return "0 MB"
    size_mb_display.short_description = 'Total Attachment Size'

    def has_add_permission(self, request):
        return False  # Don't allow manual creation


@admin.register(EmailRateLimit)
class EmailRateLimitAdmin(admin.ModelAdmin):
    list_display = ('identifier_type', 'identifier_value_short', 'emails_sent_current_hour', 'is_blocked_badge')
    list_filter = ('identifier_type', 'is_blocked', 'updated_at')
    search_fields = ('identifier_value', 'identifier_hash')
    readonly_fields = ('identifier_hash', 'created_at', 'updated_at')

    def identifier_value_short(self, obj):
        val = obj.identifier_value
        return val[:30] + ('...' if len(val) > 30 else '')
    identifier_value_short.short_description = 'Identifier'

    def is_blocked_badge(self, obj):
        if obj.is_blocked:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold;">BLOCKED</span>'
            )
        return format_html(
            '<span style="background-color: green; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">ALLOWED</span>'
        )
    is_blocked_badge.short_description = 'Status'


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'content_type', 'size_mb', 'upload_status', 'created_at')
    list_filter = ('content_type', 'upload_status', 'created_at')
    search_fields = ('filename', 'email_log__request_id')
    readonly_fields = ('created_at',)

    def size_mb(self, obj):
        return f"{obj.size_mb:.2f} MB"
    size_mb.short_description = 'Size'


@admin.register(EmailSESEvent)
class EmailSESEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_timestamp', 'bounce_type', 'email_log_link')
    list_filter = ('event_type', 'bounce_type', 'event_timestamp')
    search_fields = ('email_log__request_id', 'email_log__subject')
    readonly_fields = ('created_at', 'raw_event_data')

    def email_log_link(self, obj):
        url = reverse('admin:emails_emailsendlog_change', args=[obj.email_log.id])
        return format_html('<a href="{}">{}</a>', url, obj.email_log.request_id[:8])
    email_log_link.short_description = 'Email Log'

    def has_add_permission(self, request):
        return False  # SES events are created automatically
