"""
Utility functions for the SaaS platform.
"""
import uuid
from decimal import Decimal
from typing import Optional
from django.conf import settings


def generate_unique_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def cents_to_dollars(cents: int) -> Decimal:
    """Convert cents to dollars."""
    return Decimal(cents) / 100


def dollars_to_cents(dollars: Decimal) -> int:
    """Convert dollars to cents."""
    return int(dollars * 100)


def calculate_tax_amount(subtotal_cents: int, tax_rate: Optional[float] = None) -> int:
    """Calculate tax amount in cents."""
    if tax_rate is None:
        tax_rate = getattr(settings, 'TAX_RATE', 8.5)
    
    tax_amount = (subtotal_cents * tax_rate) / 100
    return int(tax_amount)


def calculate_discount_amount(subtotal_cents: int, discount_percent: float) -> int:
    """Calculate discount amount in cents."""
    discount_amount = (subtotal_cents * discount_percent) / 100
    return int(discount_amount)


def format_currency(amount_cents: int, currency: str = 'USD') -> str:
    """Format currency amount for display."""
    amount_dollars = cents_to_dollars(amount_cents)
    
    if currency == 'USD':
        return f"${amount_dollars:,.2f}"
    else:
        return f"{amount_dollars:,.2f} {currency}"


def generate_invoice_number() -> str:
    """Generate a unique invoice number."""
    from datetime import datetime
    year = datetime.now().year
    # This would typically use a sequence from the database
    # For now, we'll use a simple timestamp-based approach
    import time
    timestamp = int(time.time() * 1000) % 10000
    return f"INV-{year}-{timestamp:04d}" 