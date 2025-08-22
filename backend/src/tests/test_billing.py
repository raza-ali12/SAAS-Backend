"""
Tests for billing functionality.
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from src.accounts.models import User
from src.billing.models import Product, Plan, Customer, Subscription


class BillingTestCase(TestCase):
    """Test billing endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        # Create test product and plan
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            active=True
        )
        
        self.plan = Plan.objects.create(
            product=self.product,
            name='Test Plan',
            description='Test plan description',
            price_cents=1000,  # $10.00
            currency='USD',
            interval='monthly',
            trial_days=7,
            active=True
        )
        
        # Create customer
        self.customer = Customer.objects.create(
            user=self.user,
            company_name='Test Company',
            address_line1='123 Test St',
            city='Test City',
            state='TS',
            postal_code='12345',
            country='USA'
        )
    
    def test_catalog_products(self):
        """Test catalog products endpoint."""
        url = reverse('catalog-products')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Product')
    
    def test_catalog_plans(self):
        """Test catalog plans endpoint."""
        url = reverse('catalog-plans')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Plan')
    
    def test_create_subscription(self):
        """Test subscription creation."""
        self.client.force_authenticate(user=self.user)
        url = reverse('subscription-list')
        
        data = {
            'plan_id': self.plan.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plan']['id'], self.plan.id)
        
        # Check subscription was created
        subscription = Subscription.objects.get(customer=self.customer)
        self.assertEqual(subscription.plan, self.plan)
        self.assertEqual(subscription.status, 'trialing')
    
    def test_get_user_subscriptions(self):
        """Test getting user subscriptions."""
        # Create subscription
        subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            status='active',
            current_period_start='2024-01-01T00:00:00Z',
            current_period_end='2024-02-01T00:00:00Z'
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('subscription-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], subscription.id) 