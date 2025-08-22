"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from src.accounts.views import (
    register, login, logout, me, update_profile, change_password,
    AdminUserListCreateView, AdminUserDetailView
)
from src.billing.views import (
    CustomerDetailView,
    SubscriptionListCreateView, SubscriptionDetailView,
    InvoiceListView, InvoiceDetailView,
    AdminProductViewSet, AdminPlanViewSet, AdminCouponViewSet,
    AdminSubscriptionViewSet, AdminInvoiceViewSet, AdminPaymentViewSet,
    CatalogProductListView, CatalogPlanListView,
    PaymentWebhookView
)

# Create router for admin viewsets
admin_router = DefaultRouter()
admin_router.register(r'products', AdminProductViewSet)
admin_router.register(r'plans', AdminPlanViewSet)
admin_router.register(r'coupons', AdminCouponViewSet)
admin_router.register(r'subscriptions', AdminSubscriptionViewSet)
admin_router.register(r'invoices', AdminInvoiceViewSet)
admin_router.register(r'payments', AdminPaymentViewSet)

urlpatterns = [
    # Authentication
    path('auth/register/', register, name='auth-register'),
    path('auth/login/', login, name='auth-login'),
    path('auth/logout/', logout, name='auth-logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', me, name='auth-me'),
    path('auth/profile/', update_profile, name='auth-profile'),
    path('auth/change-password/', change_password, name='auth-change-password'),
    
    # Admin user management
    path('admin/users/', AdminUserListCreateView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    
    # Admin billing management
    path('admin/', include(admin_router.urls)),
    
    # Customer management
    path('customers/me/', CustomerDetailView.as_view(), name='customer-me'),
    
    # Subscriptions
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscription-list'),
    path('subscriptions/me/', SubscriptionListCreateView.as_view(), name='subscription-me'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('subscriptions/<int:pk>/cancel/', SubscriptionDetailView.as_view(), name='subscription-cancel'),
    
    # Invoices
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/me/', InvoiceListView.as_view(), name='invoice-me'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<int:pk>/pdf/', InvoiceDetailView.as_view(), name='invoice-pdf'),
    path('invoices/<int:pk>/finalize/', InvoiceDetailView.as_view(), name='invoice-finalize'),
    path('invoices/<int:pk>/pay/', InvoiceDetailView.as_view(), name='invoice-pay'),
    
    # Catalog (public)
    path('catalog/products/', CatalogProductListView.as_view(), name='catalog-products'),
    path('catalog/plans/', CatalogPlanListView.as_view(), name='catalog-plans'),
    
    # Payment webhooks
    path('payments/webhooks/<str:provider>/', PaymentWebhookView.as_view(), name='payment-webhook'),
    
    # Health check
    path('health/', lambda request: {'status': 'ok'}, name='health'),
] 