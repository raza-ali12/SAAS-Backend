# API Examples

This document provides examples of how to use the SaaS Invoice Platform API.

## Authentication

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123!"
  }'
```

### Get current user
```bash
curl -X GET http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Catalog

### Get all products
```bash
curl -X GET http://localhost:8000/api/v1/catalog/products/
```

### Get all plans
```bash
curl -X GET http://localhost:8000/api/v1/catalog/plans/
```

## Subscriptions

### Create subscription
```bash
curl -X POST http://localhost:8000/api/v1/subscriptions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": 1,
    "coupon_code": "WELCOME20"
  }'
```

### Get user subscriptions
```bash
curl -X GET http://localhost:8000/api/v1/subscriptions/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Invoices

### Get user invoices
```bash
curl -X GET http://localhost:8000/api/v1/invoices/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get invoice details
```bash
curl -X GET http://localhost:8000/api/v1/invoices/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Download invoice PDF
```bash
curl -X GET http://localhost:8000/api/v1/invoices/1/pdf/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --output invoice.pdf
```

### Pay invoice
```bash
curl -X POST http://localhost:8000/api/v1/invoices/1/pay/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Admin Endpoints

### Get all users (Admin only)
```bash
curl -X GET http://localhost:8000/api/v1/admin/users/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### Create product (Admin only)
```bash
curl -X POST http://localhost:8000/api/v1/admin/products/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Product description",
    "active": true
  }'
```

### Create plan (Admin only)
```bash
curl -X POST http://localhost:8000/api/v1/admin/plans/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "name": "Premium Plan",
    "description": "Premium features",
    "price_cents": 5000,
    "currency": "USD",
    "interval": "monthly",
    "trial_days": 7,
    "active": true
  }'
```

## Webhooks

### Payment webhook (Dummy provider)
```bash
curl -X POST http://localhost:8000/api/v1/payments/webhooks/dummy/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "payment.succeeded",
    "data": {
      "payment_id": "dummy_payment_123"
    }
  }'
```

## Error Responses

All API endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

## Pagination

List endpoints support pagination:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/invoices/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering

Many endpoints support filtering:

```bash
# Filter invoices by status
curl -X GET "http://localhost:8000/api/v1/invoices/?status=open" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter users by role
curl -X GET "http://localhost:8000/api/v1/admin/users/?role=admin" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
``` 