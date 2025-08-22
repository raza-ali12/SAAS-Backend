# Deployment Guide

This guide covers deploying the SaaS Invoice Platform to production.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (or use the included one)
- Domain name and SSL certificates
- Environment variables configured

## Production Setup

### 1. Environment Configuration

Create production environment files:

**Backend (.env):**
```env
DJANGO_SECRET_KEY=your-secure-production-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_HOST=db
DB_PORT=5432
DB_NAME=saas_prod
DB_USER=postgres
DB_PASSWORD=your-secure-db-password
REDIS_URL=redis://redis:6379/0
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
PAYMENTS_PROVIDER=dummy
SITE_URL=https://yourdomain.com
API_URL=https://yourdomain.com/api
ENABLE_CELERY=true
DEFAULT_CURRENCY=USD
DEFAULT_TIMEZONE=UTC
TAX_RATE=8.5
```

**Frontend (.env):**
```env
VITE_API_URL=https://yourdomain.com/api/v1
VITE_APP_NAME=SaaS Invoice Platform
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false
```

### 2. SSL Configuration

Create SSL certificates and configure nginx:

```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

### 3. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:5173;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx.key;

        # API endpoints
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Admin panel
        location /admin/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            proxy_pass http://backend;
        }

        # Media files
        location /media/ {
            proxy_pass http://backend;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 4. Database Setup

For production, consider using a managed PostgreSQL service:

- **AWS RDS**
- **Google Cloud SQL**
- **DigitalOcean Managed Databases**
- **Heroku Postgres**

Update the database configuration in your `.env` file accordingly.

### 5. Deploy

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## Monitoring

### Health Checks

The application includes health check endpoints:

- Backend: `GET /api/v1/health/`
- Database connectivity
- Redis connectivity

### Logs

Monitor application logs:

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Backup

Set up regular database backups:

```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres saas_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres saas_prod < backup_file.sql
```

## Scaling

### Horizontal Scaling

To scale the application:

```bash
# Scale backend workers
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale frontend instances
docker-compose -f docker-compose.prod.yml up -d --scale frontend=2
```

### Load Balancing

For high-traffic applications, consider using a load balancer:

- **AWS Application Load Balancer**
- **Google Cloud Load Balancer**
- **Nginx Plus**
- **HAProxy**

## Security

### Environment Variables

- Never commit `.env` files to version control
- Use secure secret management (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets regularly

### Database Security

- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular security updates

### Application Security

- Keep dependencies updated
- Enable HTTPS only
- Implement rate limiting
- Regular security audits

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials
   - Verify network connectivity
   - Ensure database is running

2. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check nginx configuration
   - Verify file permissions

3. **Email Not Sending**
   - Check SMTP configuration
   - Verify email credentials
   - Check firewall settings

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```env
DJANGO_DEBUG=True
```

Remember to disable it in production after resolving issues.

## Performance Optimization

### Caching

Enable Redis caching:

```env
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Database Optimization

- Add database indexes
- Optimize queries
- Use database connection pooling
- Regular maintenance

### Frontend Optimization

- Enable gzip compression
- Use CDN for static assets
- Implement lazy loading
- Optimize bundle size 