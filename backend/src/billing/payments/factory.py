"""
Payment provider factory.
"""
from django.conf import settings
from .base import PaymentProvider
from .dummy import DummyProvider
from .stripe import StripeProvider


def get_payment_provider() -> PaymentProvider:
    """
    Get the configured payment provider.
    
    Returns:
        PaymentProvider instance
        
    Raises:
        ValueError: If provider is not configured
    """
    provider_name = getattr(settings, 'PAYMENTS_PROVIDER', 'dummy')
    
    if provider_name == 'dummy':
        return DummyProvider()
    elif provider_name == 'stripe':
        return StripeProvider()
    else:
        raise ValueError(f"Unknown payment provider: {provider_name}")


def get_provider_name() -> str:
    """Get the current payment provider name."""
    return getattr(settings, 'PAYMENTS_PROVIDER', 'dummy') 