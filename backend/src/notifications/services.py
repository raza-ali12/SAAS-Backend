"""
Email notification service.
"""
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from src.billing.models import Invoice


class EmailService:
    """Service for sending email notifications."""
    
    def send_invoice_email(self, invoice: Invoice, pdf_path: str = None):
        """
        Send invoice email to customer.
        
        Args:
            invoice: Invoice object
            pdf_path: Path to PDF file (optional)
        """
        subject = f"Invoice {invoice.number} from {settings.COMPANY_NAME}"
        
        context = {
            'invoice': invoice,
            'customer': invoice.customer,
            'company_name': getattr(settings, 'COMPANY_NAME', 'SaaS Invoice Platform'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', 'billing@saas-invoice.com'),
            'company_phone': getattr(settings, 'COMPANY_PHONE', '+1 (555) 123-4567'),
        }
        
        # Render email template
        html_content = render_to_string('notifications/invoice_email.html', context)
        text_content = render_to_string('notifications/invoice_email.txt', context)
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer.user.email],
            reply_to=[getattr(settings, 'COMPANY_EMAIL', 'billing@saas-invoice.com')]
        )
        
        email.content_subtype = "html"
        
        # Attach PDF if provided
        if pdf_path:
            with open(pdf_path, 'rb') as f:
                email.attach(
                    f"invoice_{invoice.number}.pdf",
                    f.read(),
                    'application/pdf'
                )
        
        # Send email
        email.send()
    
    def send_payment_confirmation(self, payment):
        """
        Send payment confirmation email.
        
        Args:
            payment: Payment object
        """
        subject = f"Payment Confirmation - Invoice {payment.invoice.number}"
        
        context = {
            'payment': payment,
            'invoice': payment.invoice,
            'customer': payment.invoice.customer,
            'company_name': getattr(settings, 'COMPANY_NAME', 'SaaS Invoice Platform'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', 'billing@saas-invoice.com'),
        }
        
        html_content = render_to_string('notifications/payment_confirmation.html', context)
        text_content = render_to_string('notifications/payment_confirmation.txt', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[payment.invoice.customer.user.email],
            reply_to=[getattr(settings, 'COMPANY_EMAIL', 'billing@saas-invoice.com')]
        )
        
        email.content_subtype = "html"
        email.send()
    
    def send_subscription_renewal_reminder(self, subscription):
        """
        Send subscription renewal reminder.
        
        Args:
            subscription: Subscription object
        """
        subject = f"Subscription Renewal Reminder - {subscription.plan.name}"
        
        context = {
            'subscription': subscription,
            'customer': subscription.customer,
            'plan': subscription.plan,
            'company_name': getattr(settings, 'COMPANY_NAME', 'SaaS Invoice Platform'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', 'billing@saas-invoice.com'),
        }
        
        html_content = render_to_string('notifications/subscription_renewal.html', context)
        text_content = render_to_string('notifications/subscription_renewal.txt', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscription.customer.user.email],
            reply_to=[getattr(settings, 'COMPANY_EMAIL', 'billing@saas-invoice.com')]
        )
        
        email.content_subtype = "html"
        email.send()
    
    def send_welcome_email(self, user):
        """
        Send welcome email to new user.
        
        Args:
            user: User object
        """
        subject = f"Welcome to {getattr(settings, 'COMPANY_NAME', 'SaaS Invoice Platform')}"
        
        context = {
            'user': user,
            'company_name': getattr(settings, 'COMPANY_NAME', 'SaaS Invoice Platform'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', 'support@saas-invoice.com'),
        }
        
        html_content = render_to_string('notifications/welcome_email.html', context)
        text_content = render_to_string('notifications/welcome_email.txt', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            reply_to=[getattr(settings, 'COMPANY_EMAIL', 'support@saas-invoice.com')]
        )
        
        email.content_subtype = "html"
        email.send()


# Global instance
email_service = EmailService() 