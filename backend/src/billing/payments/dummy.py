"""
Dummy payment provider for testing and development.
"""
import uuid
import time
from typing import Dict, Any, Optional
from django.utils import timezone
from .base import PaymentProvider, PaymentError


class DummyProvider(PaymentProvider):
    """Dummy payment provider that simulates successful payments."""
    
    def __init__(self):
        self.payments = {}  # In-memory storage for demo purposes
    
    def create_checkout(self, invoice_or_subscription, **kwargs) -> Dict[str, Any]:
        """Create a dummy checkout session."""
        checkout_id = f"dummy_checkout_{uuid.uuid4().hex[:8]}"
        
        # Determine amount based on object type
        if hasattr(invoice_or_subscription, 'total_cents'):
            amount_cents = invoice_or_subscription.total_cents
        elif hasattr(invoice_or_subscription, 'plan'):
            amount_cents = invoice_or_subscription.plan.price_cents
        else:
            amount_cents = 0
        
        checkout_data = {
            'id': checkout_id,
            'amount_cents': amount_cents,
            'currency': getattr(invoice_or_subscription, 'currency', 'USD'),
            'status': 'open',
            'payment_url': f"https://dummy-payment.com/checkout/{checkout_id}",
            'expires_at': timezone.now() + timezone.timedelta(hours=24),
        }
        
        return checkout_data
    
    def capture_payment(self, invoice, **kwargs) -> Dict[str, Any]:
        """Capture a dummy payment."""
        payment_id = f"dummy_payment_{uuid.uuid4().hex[:8]}"
        
        # Simulate processing time
        time.sleep(0.1)
        
        payment_data = {
            'id': payment_id,
            'status': 'succeeded',
            'amount_cents': invoice.total_cents,
            'currency': invoice.currency,
            'processed_at': timezone.now(),
            'provider_ref': payment_id,
            'metadata': {
                'invoice_id': invoice.id,
                'customer_email': invoice.customer.user.email,
            }
        }
        
        # Store payment data for later reference
        self.payments[payment_id] = payment_data
        
        return payment_data
    
    def refund(self, payment, amount_cents: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Process a dummy refund."""
        refund_id = f"dummy_refund_{uuid.uuid4().hex[:8]}"
        
        # Use full amount if not specified
        if amount_cents is None:
            amount_cents = payment.amount_cents
        
        refund_data = {
            'id': refund_id,
            'status': 'succeeded',
            'amount_cents': amount_cents,
            'currency': payment.currency,
            'processed_at': timezone.now(),
            'provider_ref': refund_id,
            'metadata': {
                'payment_id': payment.provider_ref,
                'original_amount_cents': payment.amount_cents,
            }
        }
        
        return refund_data
    
    def parse_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Parse dummy webhook payload."""
        # In a real implementation, this would validate the signature
        # For dummy provider, we'll just return a success event
        
        event_data = {
            'id': f"dummy_event_{uuid.uuid4().hex[:8]}",
            'type': 'payment_intent.succeeded',
            'created': int(time.time()),
            'data': {
                'object': {
                    'id': f"dummy_payment_{uuid.uuid4().hex[:8]}",
                    'status': 'succeeded',
                    'amount': 1000,  # $10.00
                    'currency': 'usd',
                }
            }
        }
        
        return event_data
    
    def get_payment_status(self, payment_ref: str) -> str:
        """Get payment status from dummy provider."""
        # Check if payment exists in our storage
        if payment_ref in self.payments:
            return self.payments[payment_ref]['status']
        
        # For demo purposes, return a random status
        import random
        statuses = ['succeeded', 'failed', 'pending']
        return random.choice(statuses)
    
    def simulate_payment_failure(self, payment_ref: str):
        """Simulate a payment failure for testing."""
        if payment_ref in self.payments:
            self.payments[payment_ref]['status'] = 'failed'
            self.payments[payment_ref]['failure_reason'] = 'Simulated failure for testing'
    
    def simulate_payment_delay(self, payment_ref: str, delay_seconds: int = 5):
        """Simulate a delayed payment for testing."""
        if payment_ref in self.payments:
            self.payments[payment_ref]['status'] = 'pending'
            self.payments[payment_ref]['delay_until'] = timezone.now() + timezone.timedelta(seconds=delay_seconds) 