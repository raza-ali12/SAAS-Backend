# SaaS Invoice & Subscription Platform

A production-ready SaaS platform for managing invoices, subscriptions, and payments built with Django REST Framework and React.

## 🚀 Features

- **Authentication**: JWT-based auth with role-based access control (RBAC)
- **Billing**: Products, plans, coupons, subscriptions, and invoices
- **Payments**: Provider-agnostic payment system with DummyProvider (default) and optional Stripe
- **PDF Generation**: Automatic invoice PDF generation and email delivery
- **Admin Dashboard**: Complete admin interface for managing all aspects
- **API Documentation**: OpenAPI/Swagger documentation
- **Dockerized**: Full containerization with docker-compose

## 🛠️ Tech Stack

### Backend
- **Django 5.0+** with Django REST Framework
- **PostgreSQL** database
- **JWT Authentication** (access/refresh tokens)
- **Celery + Redis** (optional, for async tasks)
- **WeasyPrint** for PDF generation
- **Pytest** for testing

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **TailwindCSS** + **shadcn/ui** for styling
- **Redux Toolkit** + **RTK Query** for state management
- **React Router** for navigation
- **React Hook Form** + **Zod** for form validation

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd saas-invoice

# Copy environment files
cp backend/.env.sample backend/.env
cp frontend/.env.sample frontend/.env
```

### 2. Start with Docker (Recommended)

```bash
# Start all services
make up

# Or manually
docker-compose up -d
```

### 3. Seed Demo Data

```bash
# Seed demo data (creates admin user and sample data)
make seed

# Or manually
docker-compose exec backend python manage.py seed_demo
```

### 4. Access the Application

**Demo Admin Account:**
- Email: `admin@example.com`
- Password: `Admin123!`

**Demo Customer Account:**
- Email: `customer@example.com`
- Password: `Customer123!`

## 📋 Available Commands

```bash
# Docker commands
make up          # Start all services
make down        # Stop all services
make logs        # View logs
make restart     # Restart services

# Backend commands
make migrate     # Run migrations
make seed        # Seed demo data
make shell       # Django shell
make test        # Run tests

# Frontend commands
make frontend-dev    # Start frontend dev server
make frontend-build  # Build frontend for production
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
DB_HOST=db
DB_PORT=5432
DB_NAME=saas
DB_USER=postgres
DB_PASSWORD=postgres
REDIS_URL=redis://redis:6379/0
EMAIL_BACKEND=console
PAYMENTS_PROVIDER=dummy
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
SITE_URL=http://localhost:5173
API_URL=http://localhost:8000
ENABLE_CELERY=false
DEFAULT_CURRENCY=USD
DEFAULT_TIMEZONE=UTC
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 🏛️ API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Catalog (Admin)
- `GET/POST /api/v1/catalog/products` - Manage products
- `GET/POST /api/v1/catalog/plans` - Manage plans
- `GET/POST /api/v1/catalog/coupons` - Manage coupons

### Customers & Subscriptions
- `GET/PUT /api/v1/customers/me` - Manage customer profile
- `POST /api/v1/subscriptions` - Create subscription
- `GET /api/v1/subscriptions/me` - List user subscriptions
- `POST /api/v1/subscriptions/{id}/cancel` - Cancel subscription

### Invoices
- `GET /api/v1/invoices/me` - List user invoices
- `GET /api/v1/invoices/{id}` - Get invoice details
- `POST /api/v1/invoices/{id}/finalize` - Finalize invoice
- `GET /api/v1/invoices/{id}/pdf` - Download PDF
- `POST /api/v1/invoices/{id}/pay` - Pay invoice

### Payments
- `POST /api/v1/payments/webhooks/{provider}` - Payment webhooks

## 👥 User Roles & Permissions

### Roles
- **OWNER**: Full system access
- **ADMIN**: Manage products, plans, coupons, subscriptions, invoices, users
- **ACCOUNTANT**: Manage invoices, payments, view subscriptions
- **USER**: Manage own profile, view own invoices/subscriptions



## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test categories
docker-compose exec backend pytest billing/tests/
docker-compose exec backend pytest accounts/tests/
docker-compose exec backend pytest api/tests/
```

## 📦 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=<secure-secret>
   PAYMENTS_PROVIDER=stripe  # or keep dummy
   ```

2. **Database Migration**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. **Static Files**
   ```bash
   docker-compose exec backend python manage.py collectstatic
   ```

4. **SSL/HTTPS**: Configure reverse proxy (nginx) with SSL certificates

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Monitoring & Logging

### Health Checks
- Backend: `GET /api/v1/health/`
- Database connectivity
- Redis connectivity (if enabled)

### Logging
- Django logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs db`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

