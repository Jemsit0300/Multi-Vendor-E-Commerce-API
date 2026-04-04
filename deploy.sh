#!/bin/bash

# Quick Deployment Script for E-Commerce API
# Usage: ./deploy.sh [production|staging]

set -e

ENVIRONMENT="${1:-production}"
PROJECT_DIR="/opt/ecommerce"
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "════════════════════════════════════════════════════════"
echo "  E-Commerce API Deployment Script"
echo "  Environment: $ENVIRONMENT"
echo "════════════════════════════════════════════════════════"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root"
   exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR" || exit 1

# 1. Check required files
echo "🔍 Checking required files..."
required_files=(".env" "$COMPOSE_FILE" "nginx.conf" "requirements.txt")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Missing file: $file"
        exit 1
    fi
done
echo "✓ All required files found"

# 2. Update code from Git
echo ""
echo "📥 Pulling latest code..."
git fetch origin
git reset --hard origin/main
echo "✓ Code updated"

# 3. Build Docker images
echo ""
echo "🔨 Building Docker images..."
docker-compose -f "$COMPOSE_FILE" build --no-cache 2>&1 | tail -5
echo "✓ Build completed"

# 4. Stop running containers
echo ""
echo "🛑 Stopping running containers..."
docker-compose -f "$COMPOSE_FILE" down || true
sleep 2
echo "✓ Containers stopped"

# 5. Start containers
echo ""
echo "🚀 Starting containers..."
docker-compose -f "$COMPOSE_FILE" up -d
sleep 5
echo "✓ Containers started"

# 6. Run migrations
echo ""
echo "📊 Running database migrations..."
docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate --noinput
echo "✓ Migrations completed"

# 7. Collect static files
echo ""
echo "📦 Collecting static files..."
docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput --clear
echo "✓ Static files collected"

# 8. Check health
echo ""
echo "🏥 Checking application health..."
sleep 3

MAX_ATTEMPTS=10
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -sf http://127.0.0.1:8000/api/health/ > /dev/null; then
        echo "✓ Application is healthy"
        break
    else
        ATTEMPT=$((ATTEMPT+1))
        echo "  Waiting for application to be ready... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
        sleep 3
    fi
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ Application health check failed!"
    docker-compose -f "$COMPOSE_FILE" logs web | tail -20
    exit 1
fi

# 9. Verify containers
echo ""
echo "✅ Deployment Summary:"
echo "════════════════════════════════════════════════════════"
docker-compose -f "$COMPOSE_FILE" ps
echo "════════════════════════════════════════════════════════"

# 10. Show logs
echo ""
echo "📋 Recent application logs:"
docker-compose -f "$COMPOSE_FILE" logs --tail=10 web

echo ""
echo "✅ Deployment Completed Successfully!"
echo ""
echo "Commands for managing the application:"
echo "  View logs:     docker-compose -f $COMPOSE_FILE logs -f web"
echo "  Restart:       docker-compose -f $COMPOSE_FILE restart"
echo "  Shell access:  docker-compose -f $COMPOSE_FILE exec web bash"
echo "  Database backup: bash /opt/ecommerce/backup.sh"
echo ""
