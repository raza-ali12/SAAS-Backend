"""
Management command to seed demo data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from src.billing.models import (
    Product, Plan, Coupon, Customer, Subscription,
    Invoice, InvoiceItem
)
from src.core.utils import generate_invoice_number

User = get_user_model()


class Command(BaseCommand):
    """Seed demo data for the SaaS platform."""
    
    help = 'Seed demo data for development and testing'
    
    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write('Seeding demo data...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'OWNER',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('Admin123!')
            admin_user.save()
            self.stdout.write('✓ Created admin user: admin@example.com / Admin123!')
        else:
            self.stdout.write('✓ Admin user already exists')
        
        # Create customer user
        customer_user, created = User.objects.get_or_create(
            email='customer@example.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'USER',
            }
        )
        if created:
            customer_user.set_password('Customer123!')
            customer_user.save()
            self.stdout.write('✓ Created customer user: customer@example.com / Customer123!')
        else:
            self.stdout.write('✓ Customer user already exists')
        
        # Create products
        saas_product, created = Product.objects.get_or_create(
            name='SaaS Platform',
            defaults={
                'description': 'Complete SaaS solution for businesses',
                'active': True,
            }
        )
        if created:
            self.stdout.write('✓ Created SaaS Platform product')
        
        # Create plans
        basic_plan, created = Plan.objects.get_or_create(
            name='Basic',
            product=saas_product,
            defaults={
                'description': 'Perfect for small businesses',
                'price_cents': 900,  # $9.00
                'currency': 'USD',
                'interval': 'monthly',
                'trial_days': 14,
                'active': True,
            }
        )
        if created:
            self.stdout.write('✓ Created Basic plan ($9/month)')
        
        pro_plan, created = Plan.objects.get_or_create(
            name='Pro',
            product=saas_product,
            defaults={
                'description': 'Great for growing businesses',
                'price_cents': 2900,  # $29.00
                'currency': 'USD',
                'interval': 'monthly',
                'trial_days': 7,
                'active': True,
            }
        )
        if created:
            self.stdout.write('✓ Created Pro plan ($29/month)')
        
        enterprise_plan, created = Plan.objects.get_or_create(
            name='Enterprise',
            product=saas_product,
            defaults={
                'description': 'For large organizations',
                'price_cents': 9900,  # $99.00
                'currency': 'USD',
                'interval': 'monthly',
                'trial_days': 0,
                'active': True,
            }
        )
        if created:
            self.stdout.write('✓ Created Enterprise plan ($99/month)')
        
        # Create coupons
        welcome_coupon, created = Coupon.objects.get_or_create(
            code='WELCOME20',
            defaults={
                'description': 'Welcome discount for new customers',
                'discount_type': 'percent',
                'percent_off': 20,
                'currency': 'USD',
                'max_redemptions': 100,
                'active': True,
            }
        )
        if created:
            self.stdout.write('✓ Created WELCOME20 coupon (20% off)')
        
        # Create customer
        customer, created = Customer.objects.get_or_create(
            user=customer_user,
            defaults={
                'company_name': 'Demo Company Inc.',
                'tax_id': '12-3456789',
                'address_line1': '123 Business St',
                'address_line2': 'Suite 100',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA',
            }
        )
        if created:
            self.stdout.write('✓ Created customer profile')
        
        # Create subscription
        subscription, created = Subscription.objects.get_or_create(
            customer=customer,
            plan=pro_plan,
            defaults={
                'status': 'trialing',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=7),
                'cancel_at_period_end': False,
            }
        )
        if created:
            self.stdout.write('✓ Created trial subscription')
        
        # Create invoices
        # Invoice 1 - Paid
        invoice1, created = Invoice.objects.get_or_create(
            number='INV-2024-0001',
            defaults={
                'customer': customer,
                'subscription': subscription,
                'subtotal_cents': 2900,
                'tax_cents': 247,  # 8.5% tax
                'discount_cents': 0,
                'total_cents': 3147,
                'currency': 'USD',
                'status': 'paid',
                'issued_at': timezone.now() - timedelta(days=30),
                'due_date': timezone.now() - timedelta(days=15),
                'paid_at': timezone.now() - timedelta(days=15),
            }
        )
        if created:
            # Create invoice item
            InvoiceItem.objects.create(
                invoice=invoice1,
                description='Pro Plan - Monthly Subscription',
                quantity=1,
                unit_amount_cents=2900,
            )
            self.stdout.write('✓ Created paid invoice (INV-2024-0001)')
        
        # Invoice 2 - Open
        invoice2, created = Invoice.objects.get_or_create(
            number='INV-2024-0002',
            defaults={
                'customer': customer,
                'subscription': subscription,
                'subtotal_cents': 2900,
                'tax_cents': 247,  # 8.5% tax
                'discount_cents': 580,  # 20% discount
                'total_cents': 2567,
                'currency': 'USD',
                'status': 'open',
                'issued_at': timezone.now(),
                'due_date': timezone.now() + timedelta(days=15),
            }
        )
        if created:
            # Create invoice item
            InvoiceItem.objects.create(
                invoice=invoice2,
                description='Pro Plan - Monthly Subscription',
                quantity=1,
                unit_amount_cents=2900,
            )
            self.stdout.write('✓ Created open invoice (INV-2024-0002)')
        
        # Invoice 3 - Draft
        invoice3, created = Invoice.objects.get_or_create(
            number='INV-2024-0003',
            defaults={
                'customer': customer,
                'subscription': subscription,
                'subtotal_cents': 2900,
                'tax_cents': 0,
                'discount_cents': 0,
                'total_cents': 2900,
                'currency': 'USD',
                'status': 'draft',
                'issued_at': timezone.now(),
                'due_date': timezone.now() + timedelta(days=30),
            }
        )
        if created:
            # Create invoice item
            InvoiceItem.objects.create(
                invoice=invoice3,
                description='Pro Plan - Monthly Subscription',
                quantity=1,
                unit_amount_cents=2900,
            )
            self.stdout.write('✓ Created draft invoice (INV-2024-0003)')
        
        self.stdout.write(
            self.style.SUCCESS('✓ Demo data seeded successfully!')
        )
        self.stdout.write('\nDemo Accounts:')
        self.stdout.write('  Admin: admin@example.com / Admin123!')
        self.stdout.write('  Customer: customer@example.com / Customer123!')
        self.stdout.write('\nDemo Coupons:')
        self.stdout.write('  WELCOME20 - 20% off for new customers')
        self.stdout.write('\nDemo Plans:')
        self.stdout.write('  Basic - $9/month (14-day trial)')
        self.stdout.write('  Pro - $29/month (7-day trial)')
        self.stdout.write('  Enterprise - $99/month (no trial)') 