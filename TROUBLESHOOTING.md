# Troubleshooting & Quick Reference Guide

## 🚀 Quick Start Commands

```bash
# Navigate to project
cd /opt/ecommerce

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View service logs
docker-compose -f docker-compose.prod.yml logs -f web

# Stop application
docker-compose -f docker-compose.prod.yml down

# Start application
docker-compose -f docker-compose.prod.yml up -d

# Restart specific service
docker-compose -f docker-compose.prod.yml restart web

# SSH into web container
docker-compose -f docker-compose.prod.yml exec web bash

# Run Django management commands
docker-compose -f docker-compose.prod.yml exec web python manage.py <command>

# Database shell
docker-compose -f docker-compose.prod.yml exec db psql -U ecommerce_user -d ecommerce_prod

# Redis CLI
docker-compose -f docker-compose.prod.yml exec redis redis-cli
```

---

## 🔴 Common Issues & Solutions

### 1. **502 Bad Gateway Error**

**Symptoms:** Nginx returns 502 when accessing the app

**Diagnosis:**
```bash
# Check if web container is running
docker ps | grep ecommerce_web

# Check web container logs
docker-compose -f docker-compose.prod.yml logs web | tail -50

# Check if container is healthy
docker inspect ecommerce_web | grep -A 5 "Health"
```

**Solutions:**
```bash
# Restart the container
docker-compose -f docker-compose.prod.yml restart web

# Check Nginx configuration
sudo nginx -t

# Check if port 8000 is accessible
curl http://127.0.0.1:8000/api/health/

# Check Nginx error logs
tail -50 /var/log/nginx/ecommerce_error.log
```

---

### 2. **Database Connection Refused**

**Symptoms:** "psycopg2.OperationalError: could not connect to server"

**Diagnosis:**
```bash
# Check if database container is running and healthy
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Test connection from web container
docker-compose -f docker-compose.prod.yml exec web python -c \
  "import psycopg2; psycopg2.connect('dbname=ecommerce_prod user=ecommerce_user password=xxx host=db')"
```

**Solutions:**
```bash
# Verify .env file has correct DB credentials
cat .env | grep DB_

# Ensure DB_HOST is 'db' (Docker service name, not localhost)
# Edit .env if needed
nano .env

# Restart database container
docker-compose -f docker-compose.prod.yml restart db

# Check if database exists
docker-compose -f docker-compose.prod.yml exec db psql -U ecommerce_user -l
```

---

### 3. **Static Files Not Loading (404 Errors)**

**Symptoms:** 404 errors for `/static/` URLs

**Solutions:**
```bash
# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Check static files directory exists
ls -la /opt/ecommerce/staticfiles/

# Fix permissions
sudo chmod -R 755 /opt/ecommerce/staticfiles/
sudo chown -R appuser:appuser /opt/ecommerce/staticfiles/

# Verify Nginx config points to correct directory
grep "alias.*static" /etc/nginx/sites-available/ecommerce

# Restart Nginx
sudo systemctl restart nginx
```

---

### 4. **WebSocket Connection Fails**

**Symptoms:** Chat/notifications not working, console errors about WebSocket

**Diagnosis:**
```bash
# Check if Redis is running
docker ps | grep redis

# Check Redis connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Check Django Channels configuration
docker-compose -f docker-compose.prod.yml exec web python -c \
  "from django.conf import settings; print(settings.CHANNEL_LAYERS)"

# Check Nginx WebSocket headers are correct
grep -A 5 "Upgrade" /etc/nginx/sites-available/ecommerce
```

**Solutions:**
```bash
# Ensure REDIS_HOST in .env is 'redis'
# Edit .env if needed

# Restart Redis
docker-compose -f docker-compose.prod.yml restart redis

# Verify Nginx WebSocket configuration is correct
# Should include:
#   proxy_set_header Upgrade $http_upgrade;
#   proxy_set_header Connection "upgrade";

# Restart Nginx
sudo systemctl restart nginx

# Check logs for errors
docker-compose -f docker-compose.prod.yml logs -f web | grep -i websocket
```

---

### 5. **SSL Certificate Issues**

**Symptoms:** "SSL certificate problem" or browser security warnings

**Solutions:**
```bash
# Check certificate validity
curl -I https://your-domain.com
# or
openssl s_client -connect your-domain.com:443

# Check certificate expiration
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -dates

# Renew certificate
sudo certbot renew --verbose

# Force renewal if needed
sudo certbot renew --force-renewal

# Verify certificate path in Nginx config
sudo grep "ssl_certificate" /etc/nginx/sites-available/ecommerce

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**Automatic Renewal Check:**
```bash
# Certbot creates automatic renewal in:
sudo systemctl list-timers | grep certbot
# or
sudo ls -la /etc/cron.d/ | grep certbot
```

---

### 6. **Out of Memory or Disk Space**

**Symptoms:** Containers stop unexpectedly, 507 Insufficient Storage

**Diagnosis:**
```bash
# Check disk usage
df -h

# Check Docker volume usage
docker system df

# Check memory usage
free -h
docker stats

# Check large files/directories
du -sh /opt/ecommerce/* | sort -rh
```

**Solutions:**
```bash
# Clean up Docker images and containers
docker system prune -a

# Remove old backups
ls -lthr /opt/ecommerce/backups/ | head -20
rm /opt/ecommerce/backups/ecommerce_db_old_backup.sql.gz

# Expand disk partition (if using VM)
# Contact your hosting provider

# Increase Redis maxmemory
# Edit docker-compose.prod.yml
# command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

---

### 7. **High CPU Usage or Slow Performance**

**Diagnosis:**
```bash
# Check which process is using CPU
top

# Check Docker container stats
docker stats --no-stream

# Monitor in real-time
docker stats

# Check slow queries in Django logs
docker-compose -f docker-compose.prod.yml logs web | grep "slow"
```

**Solutions:**
```bash
# Increase Gunicorn workers
# Edit docker-compose.prod.yml
# Change: --workers 4  to: --workers 8

# Optimize database queries
# Check for N+1 queries in Django code

# Add database indices
docker-compose -f docker-compose.prod.yml exec db psql -U ecommerce_user -d ecommerce_prod
# Then run CREATE INDEX commands

# Enable caching
# Verify Redis is properly configured

# Restart with new settings
docker-compose -f docker-compose.prod.yml restart web
```

---

### 8. **502 Bad Gateway After Updates**

**Status:** Application crashes after deploying new code

**Diagnosis:**
```bash
# Check if migrations were applied
docker-compose -f docker-compose.prod.yml logs web | grep "migrate"

# Check for syntax errors
docker-compose -f docker-compose.prod.yml logs web | grep -i "error"

# Check specific app logs
docker-compose -f docker-compose.prod.yml logs web | grep "orders"  # or other app
```

**Solutions:**
```bash
# Rollback to previous version
git log --oneline | head -5
git reset --hard <previous-commit-hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Or manually run migrations (if issue is just missing migration)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Check for missing dependencies
docker-compose -f docker-compose.prod.yml exec web pip list | grep expected-package
```

---

### 9. **CORS Issues**

**Symptoms:** Frontend gets "Access denied" or CORS errors in browser console

**Solutions:**
```bash
# Check CORS configuration in Django
docker-compose -f docker-compose.prod.yml exec web python -c \
  "from django.conf import settings; print(settings.CORS_ALLOWED_ORIGINS)"

# Update .env with correct frontend URLs
nano .env
# Set: CORS_ALLOWED_ORIGINS=https://frontend.yourdomain.com,https://www.yourdomain.com

# Restart web container
docker-compose -f docker-compose.prod.yml restart web

# Test with curl
curl -H "Origin: https://frontend.yourdomain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS https://your-domain.com/api/v1/products/
```

---

### 10. **Backup/Restore Issues**

**Backup went wrong:**
```bash
# Check backup script execution
bash -x /opt/ecommerce/backup.sh

# Manual backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U ecommerce_user ecommerce_prod > /tmp/backup.sql
gzip /tmp/backup.sql

# List existing backups
ls -lh /opt/ecommerce/backups/
```

**Restore from backup:**
```bash
# Find backup file
ls -lh /opt/ecommerce/backups/ | tail -5

# Restore (stop container first)
docker-compose -f docker-compose.prod.yml down

# Restore backup
docker-compose -f docker-compose.prod.yml up -d db

# Wait for DB to be ready
sleep 5

# Restore data
docker-compose -f docker-compose.prod.yml exec db zcat /opt/ecommerce/backups/ecommerce_2024*.sql.gz | \
  psql -U ecommerce_user ecommerce_prod

# Restart all services
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 Performance Monitoring Commands

```bash
# Real-time container stats
docker stats --no-stream

# Check database size
docker-compose -f docker-compose.prod.yml exec db psql -U ecommerce_user -d ecommerce_prod -c \
  "SELECT pg_size_pretty(pg_database_size(current_database())) as size;"

# Redis memory usage
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory

# Number of Redis keys
docker-compose -f docker-compose.prod.yml exec redis redis-cli dbsize

# Check API response time
time curl https://your-domain.com/api/health/

# Monitor Nginx requests in real-time
tail -f /var/log/nginx/ecommerce_access.log | grep -v "static"

# Count requests by endpoint
tail -1000 /var/log/nginx/ecommerce_access.log | awk '{print $7}' | sort | uniq -c | sort -rn
```

---

## 🔧 Useful Django Management Commands

```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Clear cache
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c \
  "from django.core.cache import cache; cache.clear()"

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Check Django configuration
docker-compose -f docker-compose.prod.yml exec web python manage.py check

# Create backup of database via Django
docker-compose -f docker-compose.prod.yml exec db pg_dump -U ecommerce_user ecommerce_prod > backup.sql

# Run custom management command
docker-compose -f docker-compose.prod.yml exec web python manage.py <your_command>
```

---

## 📧 Email Configuration (If Issues)

```bash
# Test email sending from Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Inside shell:
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'Test Message',
    'noreply@yourdomain.com',
    ['test@example.com'],
    fail_silently=False,
)
```

---

## 🆘 Emergency Procedures

### Complete Application Down
```bash
# 1. Check all services
docker ps

# 2. Restart everything
docker-compose -f docker-compose.prod.yml restart

# 3. If still down, full restart
docker-compose -f docker-compose.prod.yml down
sleep 5
docker-compose -f docker-compose.prod.yml up -d

# 4. Check status
docker-compose -f docker-compose.prod.yml ps
```

### Database Corruption
```bash
# 1. Restore from most recent backup
bash restore-backup.sh

# 2. If no backup, check integrity
docker-compose -f docker-compose.prod.yml exec db psql -U ecommerce_user -d ecommerce_prod -c "REINDEX DATABASE ecommerce_prod;"
```

### Out of Memory (Crash)
```bash
# 1. Free cache
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# 2. Remove old logs
sudo journalctl --vacuum=100M

# 3. Remove old backups
find /opt/ecommerce/backups -mtime +7 -delete

# 4. Restart services
docker-compose -f docker-compose.prod.yml restart
```

---

## 📞 When to Escalate

Contact your hosting provider or DevOps team if:
- Hardware failures (disk errors, memory issues)
- Network connectivity problems
- SSH access lost
- Unsure about security issues
- Need to scale infrastructure

---

**Last Updated:** April 2024
