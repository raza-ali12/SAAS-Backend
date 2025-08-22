"""
Tests for payment providers.
"""
import pytest
from django.test import TestCase
from src.billing.payments.factory import get_payment_provider, get_provider_name
from src.billing.payments.dummy import DummyProvider
from src.billing.payments.base import PaymentError


class PaymentProviderTestCase(TestCase):
    """Test payment provider functionality."""
    
    def test_get_provider_name(self):
        """Test getting provider name."""
        provider_name = get_provider_name()
        self.assertEqual(provider_name, 'dummy')
    
    def test_get_dummy_provider(self):
        """Test getting dummy provider."""
        provider = get_payment_provider()
        self.assertIsInstance(provider, DummyProvider)
    
    def test_dummy_provider_create_checkout(self):
        """Test dummy provider checkout creation."""
        provider = DummyProvider()
        
        # Mock invoice object
        class MockInvoice:
            def __init__(self):
                self.total_cents = 1000
                self.currency = 'USD'
        
        invoice = MockInvoice()
        checkout_data = provider.create_checkout(invoice)
        
        self.assertIn('id', checkout_data)
        self.assertIn('amount_cents', checkout_data)
        self.assertIn('currency', checkout_data)
        self.assertIn('status', checkout_data)
        self.assertEqual(checkout_data['amount_cents'], 1000)
        self.assertEqual(checkout_data['currency'], 'USD')
    
    def test_dummy_provider_capture_payment(self):
        """Test dummy provider payment capture."""
        provider = DummyProvider()
        
        # Mock invoice object
        class MockInvoice:
            def __init__(self):
                self.total_cents = 1000
                self.currency = 'USD'
                self.id = 1
                self.customer = MockCustomer()
        
        class MockCustomer:
            def __init__(self):
                self.user = MockUser()
        
        class MockUser:
            def __init__(self):
                self.email = 'test@example.com'
        
        invoice = MockInvoice()
        payment_data = provider.capture_payment(invoice)
        
        self.assertIn('id', payment_data)
        self.assertIn('status', payment_data)
        self.assertIn('amount_cents', payment_data)
        self.assertIn('currency', payment_data)
        self.assertEqual(payment_data['status'], 'succeeded')
        self.assertEqual(payment_data['amount_cents'], 1000)
    
    def test_dummy_provider_webhook_parsing(self):
        """Test dummy provider webhook parsing."""
        provider = DummyProvider()
        
        payload = b'{"test": "data"}'
        signature = 'test_signature'
        
        event_data = provider.parse_webhook(payload, signature)
        
        self.assertIn('id', event_data)
        self.assertIn('type', event_data)
        self.assertIn('created', event_data)
        self.assertIn('data', event_data)
    
    def test_dummy_provider_payment_status(self):
        """Test dummy provider payment status."""
        provider = DummyProvider()
        
        # Test with non-existent payment
        status = provider.get_payment_status('non_existent')
        self.assertIn(status, ['succeeded', 'failed', 'pending'])
        
        # Test with existing payment
        provider.payments['test_payment'] = {'status': 'succeeded'}
        status = provider.get_payment_status('test_payment')
        self.assertEqual(status, 'succeeded') 