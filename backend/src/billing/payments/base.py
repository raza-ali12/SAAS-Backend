"""
Base payment provider interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    @abstractmethod
    def create_checkout(self, invoice_or_subscription, **kwargs) -> Dict[str, Any]:
        """
        Create a checkout session for payment.
        
        Args:
            invoice_or_subscription: Invoice or Subscription object
            **kwargs: Additional parameters
            
        Returns:
            Dict containing checkout session data
        """
        pass
    
    @abstractmethod
    def capture_payment(self, invoice, **kwargs) -> Dict[str, Any]:
        """
        Capture a payment for an invoice.
        
        Args:
            invoice: Invoice object
            **kwargs: Additional parameters
            
        Returns:
            Dict containing payment result
        """
        pass
    
    @abstractmethod
    def refund(self, payment, amount_cents: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Process a refund.
        
        Args:
            payment: Payment object
            amount_cents: Amount to refund in cents (None for full refund)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing refund result
        """
        pass
    
    @abstractmethod
    def parse_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Parse and validate webhook payload.
        
        Args:
            payload: Raw webhook payload
            signature: Webhook signature for validation
            
        Returns:
            Dict containing normalized event data
        """
        pass
    
    @abstractmethod
    def get_payment_status(self, payment_ref: str) -> str:
        """
        Get payment status from provider.
        
        Args:
            payment_ref: Payment reference from provider
            
        Returns:
            Payment status string
        """
        pass


class PaymentError(Exception):
    """Base exception for payment-related errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class PaymentProviderError(PaymentError):
    """Exception raised when payment provider encounters an error."""
    pass


class PaymentValidationError(PaymentError):
    """Exception raised when payment validation fails."""
    pass


class PaymentNotFoundError(PaymentError):
    """Exception raised when payment is not found."""
    pass 