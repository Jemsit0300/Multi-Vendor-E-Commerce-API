# Production Deployment Checklist

Use this checklist to ensure your deployment is production-ready and secure.

## ✅ Pre-Deployment Phase

### Security
- [ ] Generate strong `SECRET_KEY` (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Generate strong database password (use `openssl rand -base64 32`)
- [ ] `.env` file created and NOT committed to git
- [ ] `.env` file has 600 permissions: `chmod 600 .env`
- [ ] Removed default Django secret key from settings
- [ ] Set `DEBUG = False` in production settings
- [ ] Set `ALLOWED_HOSTS` to your actual domain(s)
- [ ] CSRF_TRUSTED_ORIGINS configured for your domain

### Database
- [ ] PostgreSQL version compatible (15+)
- [ ] Database user created with limited privileges
- [ ] Database backups directory exists: `/opt/ecommerce/backups`
- [ ] Backup script is executable: `chmod +x backup.sh`
- [ ] Database connections use SSL in production

### Static & Media Files
- [ ] `STATIC_ROOT` and `STATIC_URL` configured
- [ ] `MEDIA_ROOT` and `MEDIA_URL` configured
- [ ] Permissions set correctly: `chmod 755 staticfiles media`
- [ ] Nginx configured to serve static/media directly

### Logging
- [ ] Log directory created: `mkdir -p /app/logs`
- [ ] Log rotation configured via logrotate
- [ ] Log file permissions: `chmod 755 /app/logs`

### Environment Variables
- [ ] REDIS_HOST set to `redis` (Docker service name)
- [ ] REDIS_PORT set to `6379`
- [ ] DB_HOST set to `db` (Docker service name)
- [ ] DB_PORT set to `5432`
- [ ] DJANGO_SETTINGS_MODULE set to `config.settings.production`

---

## ✅ Docker & Containers Phase

### Docker Configuration
- [ ] Dockerfile.prod uses multi-stage build
- [ ] Base image uses non-root user (`appuser`)
- [ ] Health checks defined for all services
- [ ] Resource limits set for containers (memory, CPU)
- [ ] Volumes properly mounted (read-only where possible)

### Docker Compose
- [ ] Using `docker-compose.prod.yml`
- [ ] Services depend on healthchecks
- [ ] Ports only expose to 127.0.0.1 (not 0.0.0.0)
- [ ] Database ports not exposed to public
- [ ] Restart policies set to `unless-stopped`

### Docker Images
- [ ] Images built with `--no-cache` flag
- [ ] Image sizes reasonable (not bloated)
- [ ] Images scanned for vulnerabilities (optional)

---

## ✅ Networking & Reverse Proxy Phase

### Nginx
- [ ] Nginx config file in `/etc/nginx/sites-available/`
- [ ] Config symlinked to `/etc/nginx/sites-enabled/`
- [ ] Nginx syntax verified: `nginx -t`
- [ ] Gzip compression enabled
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Static file caching headers set

### SSL/TLS
- [ ] SSL certificate obtained from Let's Encrypt
- [ ] Certificate auto-renewal configured (certbot)
- [ ] HTTP redirects to HTTPS
- [ ] HSTS enabled and preload configured
- [ ] SSL protocols set to TLSv1.2+ only
- [ ] Strong cipher suites configured

### Firewall
- [ ] Port 22 (SSH) - restrict IP if possible
- [ ] Port 80 (HTTP) - open to world (redirect to HTTPS)
- [ ] Port 443 (HTTPS) - open to world
- [ ] All other ports closed/restricted
- [ ] DDoS protection enabled (Cloudflare, etc.)

---

## ✅ Application Ready Phase

### Django Configuration
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000`
- [ ] `SECURE_BROWSER_XSS_FILTER = True`
- [ ] `X_FRAME_OPTIONS = "DENY"`
- [ ] `SECURE_CONTENT_SECURITY_POLICY` configured
- [ ] REST_FRAMEWORK authentication configured (JWT)
- [ ] Rate limiting configured (if applicable)

### Database Optimization
- [ ] Database indices created for frequently queried columns
- [ ] Connection pooling configured (CONN_MAX_AGE)
- [ ] Atomic transactions for critical operations
- [ ] Query optimization (select_related, prefetch_related)
- [ ] Database statistics up-to-date

### Redis Configuration
- [ ] Redis persistence enabled (AOF or RDB)
- [ ] Redis maxmemory policy set
- [ ] Redis channels configured for WebSockets
- [ ] Redis cache DB separate from channel DB

### Health Checks
- [ ] `/api/health/` endpoint returns 200
- [ ] Database connection tested
- [ ] Redis connection tested
- [ ] External API dependencies checked (if any)

---

## ✅ Deployment Phase

### Pre-Deployment
- [ ] Code pushed to repository and tagged with version
- [ ] All team members notified of deployment window
- [ ] Database backup created before deployment
- [ ] Rollback plan documented

### Deployment Execution
- [ ] Run: `bash deploy.sh production`
- [ ] Migrations executed successfully
- [ ] Static files collected
- [ ] Containers health checks pass
- [ ] Application responds to requests

### Post-Deployment Tests
```bash
# Test API endpoint
curl https://your-domain.com/api/health/

# Check SSL certificate
curl -I https://your-domain.com

# Check Docker containers
docker ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web

# Check database connectivity
docker-compose -f docker-compose.prod.yml exec db psql -U <db_user> -d <db_name> -c "\dt"

# Monitor resource usage
docker stats
```

---

## ✅ Monitoring & Maintenance Phase

### Monitoring Setup
- [ ] Log monitoring tool configured (ELK, Papertrail, etc.)
- [ ] Error tracking tool configured (Sentry, Rollbar, etc.)
- [ ] Performance monitoring configured (New Relic, DataDog, etc.)
- [ ] Uptime monitoring configured (UptimeRobot, Pingdom, etc.)
- [ ] Alerts configured for critical errors

### Backups
- [ ] Database backup script runs daily
- [ ] Backups stored in `/opt/ecommerce/backups`
- [ ] Backups older than 30 days automatically deleted
- [ ] Test restore from backup weekly
- [ ] Consider offsite backup (S3, etc.)

### Maintenance
- [ ] Security updates checked weekly
- [ ] Docker images updated regularly
- [ ] Database maintenance scripts scheduled
- [ ] Log cleanup/rotation configured
- [ ] Monthly security audit scheduled

### Documentation
- [ ] Deployment documented
- [ ] API documentation updated
- [ ] Environment variables documented
- [ ] Troubleshooting guide created
- [ ] Disaster recovery plan documented

---

## 🔐 Security Hardening Checklist

- [ ] SSH key-based authentication only (no password)
- [ ] SSH non-root user configured
- [ ] Fail2ban or similar installed
- [ ] Regular security patches applied
- [ ] Unused services disabled
- [ ] File permissions hardened
- [ ] Secrets not in environment (use HashiCorp Vault if complex)
- [ ] Regular penetration testing planned
- [ ] GDPR/privacy compliance reviewed
- [ ] API rate limiting configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (Django ORM protects)
- [ ] CSRF tokens enabled
- [ ] XSS protection headers set

---

## 📊 Performance Optimization Checklist

- [ ] Database query optimization done
- [ ] Indexes on frequently searched fields
- [ ] Caching strategy implemented
- [ ] Redis memory limit set
- [ ] Gunicorn workers optimally configured
- [ ] Static file compression (gzip) enabled
- [ ] CDN configured for static assets (optional)
- [ ] Database connection pooling enabled
- [ ] N+1 queries identified and fixed
- [ ] Slow query log monitored

---

## 🚨 Rollback Procedure

If deployment fails:

```bash
# 1. Stop current containers
docker-compose -f docker-compose.prod.yml down

# 2. Checkout previous working version
git checkout <previous-tag>

# 3. Restart with previous version
docker-compose -f docker-compose.prod.yml up -d

# 4. Restore database from backup if needed
bash restore-backup.sh <backup-file>

# 5. Verify application is working
curl https://your-domain.com/api/health/

# 6. Investigate issue before re-deploying
docker-compose -f docker-compose.prod.yml logs -f web
```

---

## 📞 Support & Troubleshooting

### Common Issues

**502 Bad Gateway**
```bash
docker-compose -f docker-compose.prod.yml logs web
# Check if web container is running and healthy
docker ps
```

**Database Connection Refused**
```bash
docker-compose -f docker-compose.prod.yml logs db
# Check database credentials in .env
# Ensure DB_HOST is 'db' (Docker service name)
```

**Static Files Not Loading**
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
# Check nginx config for correct path
# Verify file permissions: chmod 755 staticfiles
```

**WebSocket Connection Failed**
- Check Redis is running: `docker ps | grep redis`
- Check Redis connection in Django logs
- Verify Nginx config has WebSocket headers
- Check CORS configuration

---

## ✅ Final Verification

When deployment is complete:

```bash
# 1. API Health Check
curl -s https://your-domain.com/api/health/ | jq .

# 2. Docker Status
docker ps | grep ecommerce

# 3. Database Status
docker-compose -f docker-compose.prod.yml exec db psql -U <user> -c "SELECT version();"

# 4. Redis Status
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# 5. Nginx Status
sudo systemctl status nginx

# 6. Certificate Valid Until
curl -s https://your-domain.com | openssl s_client 2>/dev/null | grep "Not After"
```

---

**Deployment Complete! 🎉**

Monitor the application logs for the first 24 hours and be prepared to rollback if needed.
