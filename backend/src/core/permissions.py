"""
Custom permissions for role-based access control.
"""
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins of an object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.role in ['OWNER', 'ADMIN']:
            return True
        
        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object has a customer field with user
        if hasattr(obj, 'customer') and hasattr(obj.customer, 'user'):
            return obj.customer.user == request.user
        
        return False


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        return request.user.role in ['OWNER', 'ADMIN']


class IsAccountantOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow accountant or admin users.
    """
    
    def has_permission(self, request, view):
        return request.user.role in ['OWNER', 'ADMIN', 'ACCOUNTANT']


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owner users.
    """
    
    def has_permission(self, request, view):
        return request.user.role == 'OWNER'


class CanManageInvoices(permissions.BasePermission):
    """
    Custom permission for invoice management.
    """
    
    def has_permission(self, request, view):
        return request.user.role in ['OWNER', 'ADMIN', 'ACCOUNTANT']
    
    def has_object_permission(self, request, view, obj):
        # Admin and accountant can manage all invoices
        if request.user.role in ['OWNER', 'ADMIN', 'ACCOUNTANT']:
            return True
        
        # Users can only view their own invoices
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'customer') and hasattr(obj.customer, 'user'):
                return obj.customer.user == request.user
        
        return False


class CanManageSubscriptions(permissions.BasePermission):
    """
    Custom permission for subscription management.
    """
    
    def has_permission(self, request, view):
        return request.user.role in ['OWNER', 'ADMIN']
    
    def has_object_permission(self, request, view, obj):
        # Admin can manage all subscriptions
        if request.user.role in ['OWNER', 'ADMIN']:
            return True
        
        # Users can only view their own subscriptions
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'customer') and hasattr(obj.customer, 'user'):
                return obj.customer.user == request.user
        
        return False 