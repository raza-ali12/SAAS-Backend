"""
User models for the SaaS platform.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from src.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model with role-based access control.
    """
    
    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('ADMIN', 'Admin'),
        ('ACCOUNTANT', 'Accountant'),
        ('USER', 'User'),
    ]
    
    # Override username to use email
    username = None
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name='Email address'
    )
    
    # Role-based access control
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='USER',
        verbose_name='Role'
    )
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True, verbose_name='Phone number')
    is_verified = models.BooleanField(default=False, verbose_name='Email verified')
    
    # Use email as username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_admin(self):
        """Check if user is admin or owner."""
        return self.role in ['OWNER', 'ADMIN']
    
    @property
    def is_accountant(self):
        """Check if user is accountant."""
        return self.role == 'ACCOUNTANT'
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.role in ['OWNER', 'ADMIN']
    
    @property
    def can_manage_billing(self):
        """Check if user can manage billing."""
        return self.role in ['OWNER', 'ADMIN']
    
    @property
    def can_manage_invoices(self):
        """Check if user can manage invoices."""
        return self.role in ['OWNER', 'ADMIN', 'ACCOUNTANT'] 