"""
Billing models for the SaaS platform.
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from src.core.models import TimeStampedModel
from src.accounts.models import User


class Product(TimeStampedModel):
    """Product model for SaaS offerings."""
    
    name = models.CharField(max_length=255, verbose_name='Product name')
    description = models.TextField(blank=True, verbose_name='Product description')
    active = models.BooleanField(default=True, verbose_name='Active')
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Plan(TimeStampedModel):
    """Plan model for subscription tiers."""
    
    INTERVAL_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='plans',
        verbose_name='Product'
    )
    name = models.CharField(max_length=255, verbose_name='Plan name')
    description = models.TextField(blank=True, verbose_name='Plan description')
    price_cents = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Price (cents)'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Currency'
    )
    interval = models.CharField(
        max_length=10,
        choices=INTERVAL_CHOICES,
        default='monthly',
        verbose_name='Billing interval'
    )
    trial_days = models.PositiveIntegerField(
        default=0,
        verbose_name='Trial days'
    )
    active = models.BooleanField(default=True, verbose_name='Active')
    
    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        ordering = ['product', 'price_cents']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def price_dollars(self):
        """Return price in dollars."""
        return Decimal(self.price_cents) / 100
    
    @property
    def yearly_price_cents(self):
        """Return yearly price in cents."""
        if self.interval == 'yearly':
            return self.price_cents
        return self.price_cents * 12
    
    @property
    def monthly_price_cents(self):
        """Return monthly price in cents."""
        if self.interval == 'monthly':
            return self.price_cents
        return self.price_cents // 12


class Coupon(TimeStampedModel):
    """Coupon model for discounts."""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('amount', 'Fixed amount'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Coupon code'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent',
        verbose_name='Discount type'
    )
    percent_off = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Percentage off'
    )
    amount_off_cents = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Amount off (cents)'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Currency'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expires at'
    )
    max_redemptions = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Maximum redemptions'
    )
    times_redeemed = models.PositiveIntegerField(
        default=0,
        verbose_name='Times redeemed'
    )
    active = models.BooleanField(default=True, verbose_name='Active')
    
    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        """Check if coupon is valid."""
        if not self.active:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        if self.max_redemptions and self.times_redeemed >= self.max_redemptions:
            return False
        
        return True
    
    def calculate_discount(self, amount_cents):
        """Calculate discount amount in cents."""
        if not self.is_valid():
            return 0
        
        if self.discount_type == 'percent' and self.percent_off:
            return int((amount_cents * self.percent_off) / 100)
        elif self.discount_type == 'amount' and self.amount_off_cents:
            return min(self.amount_off_cents, amount_cents)
        
        return 0


class Customer(TimeStampedModel):
    """Customer model for billing information."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name='User'
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Company name'
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tax ID'
    )
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Address line 1'
    )
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Address line 2'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='City'
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='State/Province'
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Postal code'
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Country'
    )
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return f"{self.user.email} - {self.company_name or 'No Company'}"
    
    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, parts))


class Subscription(TimeStampedModel):
    """Subscription model for customer plans."""
    
    STATUS_CHOICES = [
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Customer'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='Plan'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    current_period_start = models.DateTimeField(verbose_name='Current period start')
    current_period_end = models.DateTimeField(verbose_name='Current period end')
    cancel_at_period_end = models.BooleanField(
        default=False,
        verbose_name='Cancel at period end'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Started at')
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ended at'
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions',
        verbose_name='Applied coupon'
    )
    
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.user.email} - {self.plan.name}"
    
    def cancel(self, at_period_end=True):
        """Cancel the subscription."""
        if at_period_end:
            self.cancel_at_period_end = True
            self.save()
        else:
            self.status = 'canceled'
            self.ended_at = timezone.now()
            self.save()
    
    def is_active(self):
        """Check if subscription is active."""
        return self.status in ['trialing', 'active'] and not self.cancel_at_period_end
    
    def is_trialing(self):
        """Check if subscription is in trial."""
        return self.status == 'trialing' and timezone.now() < self.current_period_end


class Invoice(TimeStampedModel):
    """Invoice model for billing."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
        ('uncollectible', 'Uncollectible'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='Customer'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name='Subscription'
    )
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Invoice number'
    )
    subtotal_cents = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal (cents)'
    )
    tax_cents = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Tax (cents)'
    )
    discount_cents = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Discount (cents)'
    )
    total_cents = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Total (cents)'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Currency'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status'
    )
    issued_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Issued at'
    )
    due_date = models.DateTimeField(verbose_name='Due date')
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Paid at'
    )
    pdf_file = models.FileField(
        upload_to='invoices/',
        null=True,
        blank=True,
        verbose_name='PDF file'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"{self.number} - {self.customer.user.email}"
    
    @property
    def subtotal_dollars(self):
        """Return subtotal in dollars."""
        return Decimal(self.subtotal_cents) / 100
    
    @property
    def tax_dollars(self):
        """Return tax in dollars."""
        return Decimal(self.tax_cents) / 100
    
    @property
    def discount_dollars(self):
        """Return discount in dollars."""
        return Decimal(self.discount_cents) / 100
    
    @property
    def total_dollars(self):
        """Return total in dollars."""
        return Decimal(self.total_cents) / 100
    
    def finalize(self):
        """Finalize the invoice."""
        if self.status == 'draft':
            self.status = 'open'
            self.save()
    
    def mark_as_paid(self):
        """Mark invoice as paid."""
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()
    
    def void(self):
        """Void the invoice."""
        self.status = 'void'
        self.save()


class InvoiceItem(TimeStampedModel):
    """Invoice item model for line items."""
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Invoice'
    )
    description = models.CharField(max_length=255, verbose_name='Description')
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Quantity'
    )
    unit_amount_cents = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Unit amount (cents)'
    )
    
    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'
    
    def __str__(self):
        return f"{self.invoice.number} - {self.description}"
    
    @property
    def total_amount_cents(self):
        """Calculate total amount in cents."""
        return self.quantity * self.unit_amount_cents
    
    @property
    def unit_amount_dollars(self):
        """Return unit amount in dollars."""
        return Decimal(self.unit_amount_cents) / 100
    
    @property
    def total_amount_dollars(self):
        """Return total amount in dollars."""
        return Decimal(self.total_amount_cents) / 100


class Payment(TimeStampedModel):
    """Payment model for invoice payments."""
    
    PROVIDER_CHOICES = [
        ('dummy', 'Dummy'),
        ('stripe', 'Stripe'),
    ]
    
    STATUS_CHOICES = [
        ('requires_action', 'Requires Action'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Invoice'
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        verbose_name='Payment provider'
    )
    provider_ref = models.CharField(
        max_length=255,
        verbose_name='Provider reference'
    )
    amount_cents = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Amount (cents)'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Currency'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requires_action',
        verbose_name='Status'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Processed at'
    )
    failure_reason = models.TextField(
        blank=True,
        verbose_name='Failure reason'
    )
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.invoice.number} - {self.provider} - {self.status}"
    
    @property
    def amount_dollars(self):
        """Return amount in dollars."""
        return Decimal(self.amount_cents) / 100 