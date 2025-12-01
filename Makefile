# ==============================================================================
# Web Sales Analytics Pipeline - Makefile
# ==============================================================================
# This Makefile provides commands to manage the entire ETL pipeline infrastructure
# including PostgreSQL database and Apache Airflow services via Docker Compose.
#
# Quick Start:
#   make all          - Complete setup (recommended for first-time setup)
#   make up           - Start all services
#   make down         - Stop all services
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - .env file configured with required environment variables
# ==============================================================================

.PHONY: help postgres init up down ps logs-webserver logs-scheduler logs clean all restart status

# Default target - show help
help:
	@echo "======================================================================"
	@echo "  Web Sales Analytics Pipeline - Available Commands"
	@echo "======================================================================"
	@echo ""
	@echo "  🚀 SETUP & START:"
	@echo "    make all              - Complete setup (postgres + init + up)"
	@echo "    make postgres         - Start PostgreSQL database only"
	@echo "    make init             - Initialize Airflow (create admin user)"
	@echo "    make up               - Start all services (webserver + scheduler)"
	@echo ""
	@echo "  🛑 STOP & CLEAN:"
	@echo "    make down             - Stop all services (preserves data)"
	@echo "    make clean            - Stop services and DELETE all data/logs"
	@echo "    make restart          - Restart all services"
	@echo ""
	@echo "  📊 MONITORING:"
	@echo "    make ps               - Show running containers status"
	@echo "    make status           - Show detailed service status"
	@echo "    make logs-webserver   - View Airflow webserver logs"
	@echo "    make logs-scheduler   - View Airflow scheduler logs"
	@echo "    make logs             - View all service logs"
	@echo ""
	@echo "  🌐 ACCESS:"
	@echo "    Airflow UI:     http://localhost:8085"
	@echo "    PostgreSQL:     localhost:5432"
	@echo "    Credentials:    admin / admin (default)"
	@echo ""
	@echo "======================================================================"

# Start PostgreSQL database only (detached mode)
postgres:
	@echo "🐘 Starting PostgreSQL database..."
	docker compose up -d postgres
	@echo "✅ PostgreSQL is running on port 5432"

# Initialize Airflow database and create admin user
# Credentials: admin / admin
init:
	@echo "⚙️  Initializing Airflow database and creating admin user..."
	docker compose up airflow-init
	@echo "✅ Airflow initialization complete"

# Start all services (webserver, scheduler, postgres) in detached mode
up:
	@echo "🚀 Starting all Airflow services..."
	docker compose up -d
	@echo "✅ All services are running!"
	@echo "   - Airflow UI: http://localhost:8085 (admin/admin)"
	@echo "   - PostgreSQL: localhost:5432"

# Stop all running services and remove containers (but preserve volumes)
down:
	@echo "🛑 Stopping all services..."
	docker compose down
	@echo "✅ All services stopped (data preserved)"

# Stop all services and REMOVE all data (volumes, logs, plugins)
# ⚠️  WARNING: This will delete all scraped data, logs, and database!
clean:
	@echo "⚠️  WARNING: This will delete ALL data, logs, and containers!"
	@echo "   Press Ctrl+C within 3 seconds to cancel..."
	@timeout /t 3 /nobreak > nul 2>&1 || sleep 3
	@echo "🧹 Cleaning up..."
	docker compose down -v
	@if exist logs rmdir /s /q logs
	@if exist plugins rmdir /s /q plugins
	@echo "✅ Cleanup complete - all data removed"

# Show status of all containers
ps:
	@echo "📊 Container Status:"
	docker compose ps

# Show detailed status including resource usage
status:
	@echo "📊 Detailed Service Status:"
	@echo ""
	docker compose ps
	@echo ""
	@echo "🐳 Docker Container Details:"
	docker ps --filter "name=web_sales_analytic_pipeline" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View Airflow webserver logs (real-time)
logs-webserver:
	@echo "📜 Showing Airflow Webserver logs (Ctrl+C to exit)..."
	docker compose logs -f airflow-webserver

# View Airflow scheduler logs (real-time)
logs-scheduler:
	@echo "📜 Showing Airflow Scheduler logs (Ctrl+C to exit)..."
	docker compose logs -f airflow-scheduler

# View all service logs (real-time)
logs:
	@echo "📜 Showing all service logs (Ctrl+C to exit)..."
	docker compose logs -f

# Restart all services
restart:
	@echo "🔄 Restarting all services..."
	@make down
	@make up
	@echo "✅ Services restarted successfully"

# Complete setup: postgres -> init -> up
# Use this for first-time setup or after running 'make clean'
all:
	@echo "======================================================================"
	@echo "  🚀 Starting Complete Airflow Setup"
	@echo "======================================================================"
	@make postgres
	@echo ""
	@echo "⏳ Waiting 10 seconds for PostgreSQL to be ready..."
	@timeout /t 10 /nobreak > nul 2>&1 || sleep 10
	@echo ""
	@make init
	@echo ""
	@make up
	@echo ""
	@echo "======================================================================"
	@echo "  ✅ Setup Complete!"
	@echo "======================================================================"
	@echo "  🌐 Airflow UI: http://localhost:8085"
	@echo "  👤 Username: admin"
	@echo "  🔑 Password: admin"
	@echo "======================================================================"
	