"""
Stripe payment provider implementation.
"""
import stripe
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from .base import PaymentProvider, PaymentError


class StripeProvider(PaymentProvider):
    """Stripe payment provider implementation."""
    
    def __init__(self):
        if not settings.STRIPE_SECRET_KEY:
            raise PaymentError("Stripe secret key not configured")
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_checkout(self, invoice_or_subscription, **kwargs) -> Dict[str, Any]:
        """Create a Stripe checkout session."""
        try:
            # Determine amount and currency
            if hasattr(invoice_or_subscription, 'total_cents'):
                amount_cents = invoice_or_subscription.total_cents
                currency = invoice_or_subscription.currency.lower()
            elif hasattr(invoice_or_subscription, 'plan'):
                amount_cents = invoice_or_subscription.plan.price_cents
                currency = invoice_or_subscription.plan.currency.lower()
            else:
                raise PaymentError("Invalid object for checkout")
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': f"Invoice {getattr(invoice_or_subscription, 'number', '')}",
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=kwargs.get('success_url', f"{settings.SITE_URL}/payment/success"),
                cancel_url=kwargs.get('cancel_url', f"{settings.SITE_URL}/payment/cancel"),
                metadata={
                    'invoice_id': str(getattr(invoice_or_subscription, 'id', '')),
                    'customer_email': invoice_or_subscription.customer.user.email,
                }
            )
            
            return {
                'id': checkout_session.id,
                'amount_cents': amount_cents,
                'currency': currency,
                'status': checkout_session.status,
                'payment_url': checkout_session.url,
                'expires_at': timezone.datetime.fromtimestamp(checkout_session.expires_at, tz=timezone.utc),
            }
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")
    
    def capture_payment(self, invoice, **kwargs) -> Dict[str, Any]:
        """Capture a payment using Stripe PaymentIntent."""
        try:
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=invoice.total_cents,
                currency=invoice.currency.lower(),
                metadata={
                    'invoice_id': str(invoice.id),
                    'customer_email': invoice.customer.user.email,
                },
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            return {
                'id': payment_intent.id,
                'status': payment_intent.status,
                'amount_cents': payment_intent.amount,
                'currency': payment_intent.currency,
                'processed_at': timezone.now(),
                'provider_ref': payment_intent.id,
                'metadata': {
                    'invoice_id': invoice.id,
                    'customer_email': invoice.customer.user.email,
                }
            }
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")
    
    def refund(self, payment, amount_cents: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Process a refund through Stripe."""
        try:
            # Create refund
            refund_data = {
                'payment_intent': payment.provider_ref,
            }
            
            if amount_cents is not None:
                refund_data['amount'] = amount_cents
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'id': refund.id,
                'status': refund.status,
                'amount_cents': refund.amount,
                'currency': refund.currency,
                'processed_at': timezone.now(),
                'provider_ref': refund.id,
                'metadata': {
                    'payment_id': payment.provider_ref,
                    'original_amount_cents': payment.amount_cents,
                }
            }
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")
    
    def parse_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Parse and validate Stripe webhook payload."""
        try:
            if not settings.STRIPE_WEBHOOK_SECRET:
                raise PaymentError("Stripe webhook secret not configured")
            
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Normalize event data
            normalized_event = {
                'id': event.id,
                'type': event.type,
                'created': event.created,
                'data': {
                    'object': {
                        'id': event.data.object.id,
                        'status': getattr(event.data.object, 'status', None),
                        'amount': getattr(event.data.object, 'amount', None),
                        'currency': getattr(event.data.object, 'currency', None),
                    }
                }
            }
            
            return normalized_event
            
        except ValueError as e:
            raise PaymentError(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise PaymentError(f"Invalid signature: {str(e)}")
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")
    
    def get_payment_status(self, payment_ref: str) -> str:
        """Get payment status from Stripe."""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_ref)
            return payment_intent.status
        except stripe.error.StripeError:
            return 'unknown' 