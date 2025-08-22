"""
Django admin configuration for billing models.
"""
from django.contrib import admin
from src.billing.models import (
    Product, Plan, Coupon, Customer, Subscription,
    Invoice, InvoiceItem, Payment
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = ['name', 'active', 'plans_count', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def plans_count(self, obj):
        """Display count of plans."""
        return obj.plans.count()
    plans_count.short_description = 'Plans'


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Admin configuration for Plan model."""
    
    list_display = [
        'name', 'product', 'price_dollars', 'currency', 'interval',
        'trial_days', 'active', 'subscriptions_count'
    ]
    list_filter = ['active', 'interval', 'currency', 'product', 'created_at']
    search_fields = ['name', 'description', 'product__name']
    ordering = ['product', 'price_cents']
    
    def subscriptions_count(self, obj):
        """Display count of active subscriptions."""
        return obj.subscriptions.filter(status__in=['active', 'trialing']).count()
    subscriptions_count.short_description = 'Active Subscriptions'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin configuration for Coupon model."""
    
    list_display = [
        'code', 'discount_type', 'percent_off', 'amount_off_cents',
        'currency', 'active', 'is_valid', 'times_redeemed', 'expires_at'
    ]
    list_filter = ['active', 'discount_type', 'currency', 'created_at']
    search_fields = ['code', 'description']
    ordering = ['-created_at']
    
    def is_valid(self, obj):
        """Display if coupon is valid."""
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for Customer model."""
    
    list_display = [
        'user_email', 'user_name', 'company_name', 'city', 'country'
    ]
    list_filter = ['country', 'created_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'company_name', 'city', 'country'
    ]
    ordering = ['user__email']
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_name(self, obj):
        """Display user name."""
        return obj.user.full_name
    user_name.short_description = 'Name'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin configuration for Subscription model."""
    
    list_display = [
        'customer_email', 'plan_name', 'status', 'current_period_end',
        'cancel_at_period_end', 'started_at'
    ]
    list_filter = ['status', 'cancel_at_period_end', 'plan__interval', 'created_at']
    search_fields = [
        'customer__user__email', 'plan__name', 'plan__product__name'
    ]
    ordering = ['-created_at']
    
    def customer_email(self, obj):
        """Display customer email."""
        return obj.customer.user.email
    customer_email.short_description = 'Customer'
    
    def plan_name(self, obj):
        """Display plan name."""
        return f"{obj.plan.product.name} - {obj.plan.name}"
    plan_name.short_description = 'Plan'


class InvoiceItemInline(admin.TabularInline):
    """Inline admin for InvoiceItem."""
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_amount_cents']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model."""
    
    list_display = [
        'number', 'customer_email', 'status', 'total_dollars',
        'currency', 'issued_at', 'due_date', 'paid_at'
    ]
    list_filter = ['status', 'currency', 'issued_at', 'due_date']
    search_fields = [
        'number', 'customer__user__email', 'customer__company_name'
    ]
    ordering = ['-issued_at']
    inlines = [InvoiceItemInline]
    
    def customer_email(self, obj):
        """Display customer email."""
        return obj.customer.user.email
    customer_email.short_description = 'Customer'
    
    def total_dollars(self, obj):
        """Display total in dollars."""
        return f"${obj.total_dollars:,.2f}"
    total_dollars.short_description = 'Total'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    
    list_display = [
        'invoice_number', 'provider', 'amount_dollars', 'currency',
        'status', 'processed_at'
    ]
    list_filter = ['provider', 'status', 'currency', 'created_at']
    search_fields = ['invoice__number', 'provider_ref']
    ordering = ['-created_at']
    
    def invoice_number(self, obj):
        """Display invoice number."""
        return obj.invoice.number
    invoice_number.short_description = 'Invoice'
    
    def amount_dollars(self, obj):
        """Display amount in dollars."""
        return f"${obj.amount_dollars:,.2f}"
    amount_dollars.short_description = 'Amount' 