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

# Set to 1 to run airflow-init with 'make all', 0 to skip it
SETUP_INCLUDED ?= 1

.PHONY: help init up down ps logs-api logs-scheduler logs clean all restart status

# Default target - show help
help:
	@echo "======================================================================"
	@echo "  Web Sales Analytics Pipeline - Available Commands"
	@echo "======================================================================"
	@echo ""
	@echo "  🚀 SETUP & START:"
	@echo "    make all              - Start services (SETUP_INCLUDED=$(SETUP_INCLUDED))"
	@echo "    make all SETUP_INCLUDED=1  - Start with init"
	@echo "    make init             - Initialize Airflow (create admin user)"
	@echo "    make up               - Start all services"
	@echo ""
	@echo "  🛑 STOP & CLEAN:"
	@echo "    make down             - Stop all services (preserves data)"
	@echo "    make clean            - Stop services and DELETE all data/logs"
	@echo "    make restart          - Restart all services"
	@echo ""
	@echo "  📊 MONITORING:"
	@echo "    make ps               - Show running containers status"
	@echo "    make status           - Show detailed service status"
	@echo "    make logs-api         - View Airflow API server logs"
	@echo "    make logs-scheduler   - View Airflow scheduler logs"
	@echo "    make logs             - View all service logs"
	@echo ""
	@echo "  🌐 ACCESS:"
	@echo "    Airflow UI:     http://localhost:8080"
	@echo "    PostgreSQL:     localhost:5432"
	@echo "    Credentials:    airflow / airflow (default)"
	@echo ""
	@echo "======================================================================"

# Initialize Airflow database and create admin user
init:
	@echo "⚙️  Initializing Airflow database and creating admin user..."
	docker compose run --rm airflow-init
	@echo "✅ Airflow initialization complete"

# Start all services in detached mode
up:
	@echo "🚀 Starting all Airflow services..."
	docker compose up -d
	@echo "✅ All services are running!"
	@echo "   - Airflow UI: http://localhost:8080 (airflow/airflow)"
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
	@if exist airflow\logs rmdir /s /q airflow\logs
	@if exist airflow\plugins rmdir /s /q airflow\plugins
	@if exist airflow\config rmdir /s /q airflow\config
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

# View Airflow API server logs (real-time)
logs-api:
	@echo "📜 Showing Airflow API Server logs (Ctrl+C to exit)..."
	docker compose logs -f airflow-apiserver

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

# Complete setup with optional init
# Use: make all SETUP_INCLUDED=1 to include init
all:
	@echo "======================================================================"
	@echo "  🚀 Starting Complete Airflow Setup"
	@echo "======================================================================"
ifeq ($(SETUP_INCLUDED),1)
	@echo "  📋 Running initialization..."
	@make init
endif
	@echo ""
	@echo "⏳ Waiting 5 seconds before starting services..."
	@timeout /t 5 /nobreak > nul 2>&1 || sleep 5
	@echo ""
	@make up
	@echo ""
	@echo "======================================================================"
	@echo "  ✅ Setup Complete!"
	@echo "======================================================================"
	@echo "  🌐 Airflow UI: http://localhost:8080"
	@echo "  👤 Username: airflow"
	@echo "  🔑 Password: airflow"
ifeq ($(SETUP_INCLUDED),0)
	@echo "  ℹ️  Note: Run 'make init' first if this is a fresh setup"
endif
	@echo "======================================================================"