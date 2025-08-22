.PHONY: help up down restart logs migrate seed shell test clean frontend-dev frontend-build frontend-install backend-install install

# Default target
help:
	@echo "SaaS Invoice & Subscription Platform - Available Commands:"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Remove all containers and volumes"
	@echo ""
	@echo "Backend Commands:"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed demo data"
	@echo "  make shell       - Open Django shell"
	@echo "  make test        - Run all tests"
	@echo "  make backend-install - Install backend dependencies"
	@echo ""
	@echo "Frontend Commands:"
	@echo "  make frontend-dev    - Start frontend development server"
	@echo "  make frontend-build  - Build frontend for production"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make setup       - Initial setup (copy env files, install deps)"

# Docker commands
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started! Access at:"
	@echo "  Frontend: http://localhost:5173"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Admin:    http://localhost:8000/admin"
	@echo "  API Docs: http://localhost:8000/api/docs"

down:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

logs:
	@echo "Showing logs from all services..."
	docker-compose logs -f

clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Backend commands
migrate:
	@echo "Running database migrations..."
	docker-compose exec backend python manage.py migrate

seed:
	@echo "Seeding demo data..."
	docker-compose exec backend python manage.py seed_demo

shell:
	@echo "Opening Django shell..."
	docker-compose exec backend python manage.py shell

test:
	@echo "Running tests..."
	docker-compose exec backend pytest

backend-install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

# Frontend commands
frontend-dev:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

frontend-build:
	@echo "Building frontend for production..."
	cd frontend && npm run build

frontend-install:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development setup
install: backend-install frontend-install
	@echo "All dependencies installed!"

setup:
	@echo "Setting up the project..."
	@if [ ! -f backend/.env ]; then \
		echo "Copying backend environment file..."; \
		cp backend/.env.sample backend/.env; \
	fi
	@if [ ! -f frontend/.env ]; then \
		echo "Copying frontend environment file..."; \
		cp frontend/.env.sample frontend/.env; \
	fi
	@echo "Running initial setup..."
	make install
	@echo "Setup complete! Run 'make up' to start services."

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/api/v1/health/ || echo "Backend not responding"
	@curl -f http://localhost:5173 || echo "Frontend not responding"

# Database commands
db-backup:
	@echo "Creating database backup..."
	docker-compose exec db pg_dump -U postgres saas > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file; \
	docker-compose exec -T db psql -U postgres saas < $$backup_file

# Production commands
prod-build:
	@echo "Building production images..."
	docker-compose -f docker-compose.prod.yml build

prod-up:
	@echo "Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	@echo "Stopping production services..."
	docker-compose -f docker-compose.prod.yml down

# Utility commands
status:
	@echo "Service status:"
	@docker-compose ps

logs-backend:
	@echo "Backend logs:"
	@docker-compose logs backend

logs-frontend:
	@echo "Frontend logs:"
	@docker-compose logs frontend

logs-db:
	@echo "Database logs:"
	@docker-compose logs db

# Development helpers
create-superuser:
	@echo "Creating superuser..."
	docker-compose exec backend python manage.py createsuperuser

collectstatic:
	@echo "Collecting static files..."
	docker-compose exec backend python manage.py collectstatic --noinput

makemigrations:
	@echo "Creating migrations..."
	docker-compose exec backend python manage.py makemigrations

# Linting and formatting
lint-backend:
	@echo "Linting backend code..."
	docker-compose exec backend flake8 .
	docker-compose exec backend black --check .
	docker-compose exec backend isort --check-only .

format-backend:
	@echo "Formatting backend code..."
	docker-compose exec backend black .
	docker-compose exec backend isort .

lint-frontend:
	@echo "Linting frontend code..."
	cd frontend && npm run lint

format-frontend:
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# All linting
lint: lint-backend lint-frontend
format: format-backend format-frontend 