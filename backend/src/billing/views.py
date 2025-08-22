"""
Views for billing models.
"""
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from src.billing.models import (
    Product, Plan, Coupon, Customer, Subscription,
    Invoice, InvoiceItem, Payment
)
from src.billing.serializers import (
    ProductSerializer, PlanSerializer, CouponSerializer, CustomerSerializer,
    SubscriptionSerializer, InvoiceSerializer, PaymentSerializer,
    AdminProductSerializer, AdminPlanSerializer, AdminCouponSerializer,
    AdminSubscriptionSerializer, AdminInvoiceSerializer, AdminPaymentSerializer
)
from src.core.permissions import (
    IsAdminUser, IsAccountantOrAdmin, CanManageInvoices,
    CanManageSubscriptions, IsOwnerOrAdmin
)
from src.billing.payments.factory import get_payment_provider
from src.core.utils import generate_invoice_number, calculate_tax_amount


# Customer Views
class CustomerDetailView(generics.RetrieveUpdateAPIView):
    """Customer profile management."""
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get customer for current user."""
        return get_object_or_404(Customer, user=self.request.user)


# Subscription Views
class SubscriptionListCreateView(generics.ListCreateAPIView):
    """List and create subscriptions."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter subscriptions by user."""
        if self.request.user.is_admin:
            return Subscription.objects.all()
        return Subscription.objects.filter(customer__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create subscription with proper setup."""
        with transaction.atomic():
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                user=self.request.user,
                defaults={'company_name': f"{self.request.user.first_name}'s Company"}
            )
            
            # Get plan
            plan = get_object_or_404(Plan, id=serializer.validated_data['plan_id'])
            
            # Check for coupon
            coupon = None
            coupon_code = serializer.validated_data.get('coupon_code')
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, active=True)
                    if not coupon.is_valid():
                        raise Coupon.DoesNotExist
                except Coupon.DoesNotExist:
                    raise serializers.ValidationError("Invalid or expired coupon code")
            
            # Calculate period dates
            now = timezone.now()
            if plan.interval == 'monthly':
                period_end = now + timezone.timedelta(days=30)
            else:  # yearly
                period_end = now + timezone.timedelta(days=365)
            
            # Set status based on trial
            status = 'trialing' if plan.trial_days > 0 else 'active'
            
            # Create subscription
            subscription = serializer.save(
                customer=customer,
                plan=plan,
                coupon=coupon,
                status=status,
                current_period_start=now,
                current_period_end=period_end
            )
            
            # Increment coupon usage
            if coupon:
                coupon.times_redeemed += 1
                coupon.save()


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Subscription detail management."""
    serializer_class = SubscriptionSerializer
    permission_classes = [CanManageSubscriptions]
    
    def get_queryset(self):
        """Filter subscriptions by user."""
        if self.request.user.is_admin:
            return Subscription.objects.all()
        return Subscription.objects.filter(customer__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel subscription."""
        subscription = self.get_object()
        at_period_end = request.data.get('cancel_at_period_end', True)
        subscription.cancel(at_period_end=at_period_end)
        
        return Response({
            'message': 'Subscription canceled successfully'
        })


# Invoice Views
class InvoiceListView(generics.ListAPIView):
    """List invoices for current user."""
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter invoices by user."""
        if self.request.user.is_admin:
            return Invoice.objects.all()
        return Invoice.objects.filter(customer__user=self.request.user)


class InvoiceDetailView(generics.RetrieveAPIView):
    """Invoice detail view."""
    serializer_class = InvoiceSerializer
    permission_classes = [CanManageInvoices]
    
    def get_queryset(self):
        """Filter invoices by user."""
        if self.request.user.is_admin:
            return Invoice.objects.all()
        return Invoice.objects.filter(customer__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Download invoice PDF."""
        invoice = self.get_object()
        
        if invoice.pdf_file:
            response = HttpResponse(invoice.pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{invoice.number}.pdf"'
            return response
        else:
            return Response({
                'error': 'PDF not generated yet'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """Finalize invoice."""
        invoice = self.get_object()
        
        if invoice.status != 'draft':
            return Response({
                'error': 'Invoice is not in draft status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate totals
        subtotal_cents = sum(item.total_amount_cents for item in invoice.items.all())
        tax_cents = calculate_tax_amount(subtotal_cents)
        discount_cents = invoice.discount_cents
        total_cents = subtotal_cents + tax_cents - discount_cents
        
        # Update invoice
        invoice.subtotal_cents = subtotal_cents
        invoice.tax_cents = tax_cents
        invoice.total_cents = total_cents
        invoice.finalize()
        
        return Response({
            'message': 'Invoice finalized successfully',
            'invoice': InvoiceSerializer(invoice).data
        })
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """Process payment for invoice."""
        invoice = self.get_object()
        
        if invoice.status != 'open':
            return Response({
                'error': 'Invoice is not open for payment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get payment provider
            provider = get_payment_provider()
            
            # Process payment
            payment_data = provider.capture_payment(invoice)
            
            # Create payment record
            payment = Payment.objects.create(
                invoice=invoice,
                provider=payment_data['provider_ref'][:20],  # Truncate if needed
                provider_ref=payment_data['provider_ref'],
                amount_cents=payment_data['amount_cents'],
                currency=payment_data['currency'],
                status=payment_data['status'],
                processed_at=payment_data.get('processed_at', timezone.now())
            )
            
            # Update invoice status
            if payment_data['status'] == 'succeeded':
                invoice.mark_as_paid()
            
            return Response({
                'message': 'Payment processed successfully',
                'payment': PaymentSerializer(payment).data
            })
            
        except Exception as e:
            return Response({
                'error': f'Payment failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


# Admin Views
class AdminProductViewSet(viewsets.ModelViewSet):
    """Admin viewset for Product management."""
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Use different serializer for list view."""
        if self.action == 'list':
            return ProductSerializer
        return AdminProductSerializer


class AdminPlanViewSet(viewsets.ModelViewSet):
    """Admin viewset for Plan management."""
    queryset = Plan.objects.all()
    serializer_class = AdminPlanSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Use different serializer for list view."""
        if self.action == 'list':
            return PlanSerializer
        return AdminPlanSerializer


class AdminCouponViewSet(viewsets.ModelViewSet):
    """Admin viewset for Coupon management."""
    queryset = Coupon.objects.all()
    serializer_class = AdminCouponSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Use different serializer for list view."""
        if self.action == 'list':
            return CouponSerializer
        return AdminCouponSerializer


class AdminSubscriptionViewSet(viewsets.ModelViewSet):
    """Admin viewset for Subscription management."""
    queryset = Subscription.objects.all()
    serializer_class = AdminSubscriptionSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Use different serializer for list view."""
        if self.action == 'list':
            return SubscriptionSerializer
        return AdminSubscriptionSerializer


class AdminInvoiceViewSet(viewsets.ModelViewSet):
    """Admin viewset for Invoice management."""
    queryset = Invoice.objects.all()
    serializer_class = AdminInvoiceSerializer
    permission_classes = [IsAccountantOrAdmin]
    
    def get_serializer_class(self):
        """Use different serializer for list view."""
        if self.action == 'list':
            return InvoiceSerializer
        return AdminInvoiceSerializer


class AdminPaymentViewSet(viewsets.ModelViewSet):
    """Admin viewset for Payment management."""
    queryset = Payment.objects.all()
    serializer_class = AdminPaymentSerializer
    permission_classes = [IsAccountantOrAdmin]
    
    def get_serializer_class(self):
        """Use different serializer for list view."""
        if self.action == 'list':
            return PaymentSerializer
        return AdminPaymentSerializer


# Catalog Views (Public)
class CatalogProductListView(generics.ListAPIView):
    """Public catalog of products."""
    serializer_class = ProductSerializer
    permission_classes = []
    
    def get_queryset(self):
        """Only show active products."""
        return Product.objects.filter(active=True)


class CatalogPlanListView(generics.ListAPIView):
    """Public catalog of plans."""
    serializer_class = PlanSerializer
    permission_classes = []
    
    def get_queryset(self):
        """Only show active plans."""
        return Plan.objects.filter(active=True, product__active=True)


# Webhook Views
class PaymentWebhookView(generics.CreateAPIView):
    """Handle payment webhooks."""
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        """Process webhook from payment provider."""
        provider_name = kwargs.get('provider')
        
        try:
            provider = get_payment_provider()
            
            # Parse webhook
            payload = request.body
            signature = request.headers.get('X-Signature', '')
            
            event_data = provider.parse_webhook(payload, signature)
            
            # Process the event
            self.process_webhook_event(event_data)
            
            return Response({'status': 'success'})
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def process_webhook_event(self, event_data):
        """Process webhook event data."""
        event_type = event_data.get('type')
        
        if event_type == 'payment_intent.succeeded':
            # Handle successful payment
            payment_id = event_data['data']['object']['id']
            # Update payment status, etc.
            pass
        elif event_type == 'payment_intent.payment_failed':
            # Handle failed payment
            pass 