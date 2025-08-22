"""
Serializers for billing models.
"""
from rest_framework import serializers
from src.billing.models import (
    Product, Plan, Coupon, Customer, Subscription,
    Invoice, InvoiceItem, Payment
)
from src.core.utils import format_currency


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for Plan model."""
    
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    price_dollars = serializers.SerializerMethodField()
    yearly_price_cents = serializers.ReadOnlyField()
    monthly_price_cents = serializers.ReadOnlyField()
    
    class Meta:
        model = Plan
        fields = [
            'id', 'product', 'product_id', 'name', 'description',
            'price_cents', 'price_dollars', 'currency', 'interval',
            'trial_days', 'active', 'yearly_price_cents', 'monthly_price_cents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_price_dollars(self, obj):
        """Format price in dollars."""
        return format_currency(obj.price_cents, obj.currency)


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model."""
    
    is_valid = serializers.ReadOnlyField()
    amount_off_dollars = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'percent_off',
            'amount_off_cents', 'amount_off_dollars', 'currency',
            'expires_at', 'max_redemptions', 'times_redeemed',
            'active', 'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'times_redeemed', 'created_at', 'updated_at']
    
    def get_amount_off_dollars(self, obj):
        """Format amount off in dollars."""
        if obj.amount_off_cents:
            return format_currency(obj.amount_off_cents, obj.currency)
        return None


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'user_email', 'user_name', 'company_name', 'tax_id',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    customer = CustomerSerializer(read_only=True)
    coupon = CouponSerializer(read_only=True)
    coupon_code = serializers.CharField(write_only=True, required=False)
    is_active = serializers.ReadOnlyField()
    is_trialing = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'customer', 'plan', 'plan_id', 'status',
            'current_period_start', 'current_period_end',
            'cancel_at_period_end', 'started_at', 'ended_at',
            'coupon', 'coupon_code', 'is_active', 'is_trialing',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'started_at', 'created_at', 'updated_at']


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model."""
    
    unit_amount_dollars = serializers.SerializerMethodField()
    total_amount_cents = serializers.ReadOnlyField()
    total_amount_dollars = serializers.SerializerMethodField()
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'description', 'quantity', 'unit_amount_cents',
            'unit_amount_dollars', 'total_amount_cents', 'total_amount_dollars'
        ]
        read_only_fields = ['id', 'total_amount_cents']
    
    def get_unit_amount_dollars(self, obj):
        """Format unit amount in dollars."""
        return format_currency(obj.unit_amount_cents, 'USD')
    
    def get_total_amount_dollars(self, obj):
        """Format total amount in dollars."""
        return format_currency(obj.total_amount_cents, 'USD')


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    
    customer = CustomerSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    subtotal_dollars = serializers.SerializerMethodField()
    tax_dollars = serializers.SerializerMethodField()
    discount_dollars = serializers.SerializerMethodField()
    total_dollars = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'customer', 'subscription', 'number', 'subtotal_cents',
            'subtotal_dollars', 'tax_cents', 'tax_dollars', 'discount_cents',
            'discount_dollars', 'total_cents', 'total_dollars', 'currency',
            'status', 'issued_at', 'due_date', 'paid_at', 'pdf_file',
            'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer', 'subscription', 'number', 'issued_at',
            'paid_at', 'pdf_file', 'created_at', 'updated_at'
        ]
    
    def get_subtotal_dollars(self, obj):
        """Format subtotal in dollars."""
        return format_currency(obj.subtotal_cents, obj.currency)
    
    def get_tax_dollars(self, obj):
        """Format tax in dollars."""
        return format_currency(obj.tax_cents, obj.currency)
    
    def get_discount_dollars(self, obj):
        """Format discount in dollars."""
        return format_currency(obj.discount_cents, obj.currency)
    
    def get_total_dollars(self, obj):
        """Format total in dollars."""
        return format_currency(obj.total_cents, obj.currency)


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    invoice = InvoiceSerializer(read_only=True)
    amount_dollars = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'provider', 'provider_ref', 'amount_cents',
            'amount_dollars', 'currency', 'status', 'processed_at',
            'failure_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice', 'provider_ref', 'processed_at',
            'created_at', 'updated_at'
        ]
    
    def get_amount_dollars(self, obj):
        """Format amount in dollars."""
        return format_currency(obj.amount_cents, obj.currency)


# Admin serializers for full CRUD operations
class AdminProductSerializer(serializers.ModelSerializer):
    """Admin serializer for Product model."""
    
    plans_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_plans_count(self, obj):
        """Get count of plans for this product."""
        return obj.plans.count()


class AdminPlanSerializer(serializers.ModelSerializer):
    """Admin serializer for Plan model."""
    
    subscriptions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Plan
        fields = '__all__'
    
    def get_subscriptions_count(self, obj):
        """Get count of active subscriptions for this plan."""
        return obj.subscriptions.filter(status__in=['active', 'trialing']).count()


class AdminCouponSerializer(serializers.ModelSerializer):
    """Admin serializer for Coupon model."""
    
    class Meta:
        model = Coupon
        fields = '__all__'


class AdminSubscriptionSerializer(serializers.ModelSerializer):
    """Admin serializer for Subscription model."""
    
    class Meta:
        model = Subscription
        fields = '__all__'


class AdminInvoiceSerializer(serializers.ModelSerializer):
    """Admin serializer for Invoice model."""
    
    class Meta:
        model = Invoice
        fields = '__all__'


class AdminPaymentSerializer(serializers.ModelSerializer):
    """Admin serializer for Payment model."""
    
    class Meta:
        model = Payment
        fields = '__all__' 