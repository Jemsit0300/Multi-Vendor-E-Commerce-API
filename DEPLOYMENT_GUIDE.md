# Professional Deployment Guide - Multi-Vendor Ecommerce API

## 📋 Ön Koşullar

- Ubuntu 22.04 LTS (veya 20.04) - Virtual Server
- Public IP Adresi
- Domain Adı (opsiyonel ama önerilir)
- SSH Erişimi
- root veya sudo yetkisi

---

## 🎯 Deployment Adımları

## PHASE 1: Server Hazırlığı (İlk Ayar)

### **Adım 1: Sistem Paketlerini Güncelle**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git python3-pip python3-venv python3-dev
sudo apt install -y build-essential libpq-dev postgresql-client
```

### **Adım 2: Docker & Docker Compose Yükle**
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Doğrulama
docker --version
docker-compose --version
```

### **Adım 3: Proje Klasörünü Hazırla**
```bash
mkdir -p /opt/ecommerce
cd /opt/ecommerce
git clone <YOUR_REPO_URL> .
```

---

## PHASE 2: Environment Variables (Yapılandırma)

### **Adım 4: .env Dosyası Oluştur**
```bash
sudo nano .env
```

**İçeriği (Security Best Practices ile):**
```env
# Django Settings
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key-here-min-50-chars-random-string-generate-with-uuid
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,server-ip-address

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_prod
DB_USER=ecommerce_user
DB_PASSWORD=VERY-STRONG-PASSWORD-HERE-MIN-20-CHARS
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_CHANNEL_DB=0
REDIS_CACHE_DB=1

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS (Frontend URL)
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Email (Optional - Production İçin)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

**Güvenlik:**
```bash
# .env Dosyasını Protekt Et
sudo chmod 600 .env
sudo chown root:root .env
```

---

## PHASE 3: Docker Compose Konfigürasyonu

### **Adım 5: Production Docker Compose Dosyası**
Aşağıdaki dosya: `docker-compose.prod.yml` oluştur

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: ecommerce_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"  # Sadece internal erişim
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ecommerce_redis
    ports:
      - "127.0.0.1:6379:6379"  # Sadece internal erişim
    restart: unless-stopped
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    container_name: ecommerce_web
    command: >
      sh -c "
        python manage.py migrate &&
        python manage.py collectstatic --noinput &&
        gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4 --worker-class sync --timeout 120 --access-logfile - --error-logfile -
      "
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
      - ./logs:/app/logs
    ports:
      - "127.0.0.1:8000:8000"  # Sadece localhost'tan
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  default:
    name: ecommerce_network
```

---

## PHASE 4: Nginx Reverse Proxy

### **Adım 6: Nginx Yükle ve Konfigüre Et**
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

**Nginx Config: `/etc/nginx/sites-available/ecommerce`**
```nginx
upstream ecommerce_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    client_max_body_size 100M;

    # HTTPS'e yönlendir
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    client_max_body_size 100M;

    # SSL Sertifikatları (Certbot sonra eklenecek)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL Best Practices
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/ecommerce_access.log;
    error_log /var/log/nginx/ecommerce_error.log;

    location / {
        proxy_pass http://ecommerce_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Connection "Upgrade";
        proxy_buffering off;
    }

    location /static/ {
        alias /opt/ecommerce/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/ecommerce/media/;
        expires 7d;
    }
}
```

**Nginx Konfigürasyonunu Aktifleştir:**
```bash
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## PHASE 5: SSL Sertifikası (HTTPS)

### **Adım 7: Let's Encrypt SSL Sertifikası**
```bash
# DNS'inde domain'inizi server IP'sine yönlendirin (A record)
# Sonra:
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run

# Sistemde cron job otomatik olarak oluşturulacak
```

---

## PHASE 6: Django Production Hazırlığı

### **Adım 8: Settings Dosyasını Doğrula**

Edit: `config/settings/production.py`

```python
# Emin ol ki şunlar doğru ayarlanmış:
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database Config
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,  # Transaction safety
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# Redis Configuration
REDIS_URL = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_CACHE_DB')}"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}
    }
}

# Session Store
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
```

---

## PHASE 7: Dockerfile Optimization

### **Adım 9: Production Dockerfile**

```dockerfile
# Build Stage
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime Stage
FROM python:3.11-slim

WORKDIR /app

# Security: Non-root user
RUN useradd -m -u 1000 appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

CMD ["gunicorn", "config.asgi:application", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

---

## PHASE 8: Health Check Endpoint

### **Adım 10: Health Check Ekle**

File: `config/urls.py` - URL'lere ekle
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def health_check(request):
    return JsonResponse({'status': 'healthy', 'message': 'API is running'})

# urls.py içine:
urlpatterns = [
    path('api/health/', health_check, name='health_check'),
    # ... rest of patterns
]
```

---

## PHASE 9: Database Backup Strategy

### **Adım 11: Otomatik Backup Script**

File: `/opt/ecommerce/backup.sh`
```bash
#!/bin/bash

BACKUP_DIR="/opt/ecommerce/backups"
DB_CONTAINER="ecommerce_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ecommerce_$TIMESTAMP.sql.gz"

mkdir -p $BACKUP_DIR

# Database backup
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Retention policy: Keep last 30 days
find $BACKUP_DIR -name "ecommerce_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Cron Job (Daily at 2 AM):**
```bash
sudo crontab -e

# Ekle:
0 2 * * * /opt/ecommerce/backup.sh >> /var/log/ecommerce_backup.log 2>&1
```

---

## PHASE 10: Monitoring ve Logging

### **Adım 12: Log Rotation**

File: `/etc/logrotate.d/ecommerce`
```
/opt/ecommerce/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 appuser appuser
    sharedscripts
    postrotate
        docker exec ecommerce_web kill -SIGUSR1 1 > /dev/null 2>&1 || true
    endscript
}
```

### **Adım 13: Systemd Service (Auto-start)**

File: `/etc/systemd/system/ecommerce.service`
```ini
[Unit]
Description=E-commerce API Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/ecommerce
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
RemainAfterExit=yes
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

**Aktifleştir:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ecommerce.service
sudo systemctl start ecommerce.service
sudo systemctl status ecommerce.service
```

---

## PHASE 11: Deployment Adımları (Final)

### **Adım 14: Deployment Checklist**

```bash
# 1. Terminal'de, sunucuya SSH yap
ssh root@YOUR_SERVER_IP

# 2. Projeyi indir
cd /opt/ecommerce
git pull origin main

# 3. Production .env dosyasını oluştur
# (Yukarıdaki şablonu kullan)

# 4. Docker imajını build et
docker-compose -f docker-compose.prod.yml build

# 5. Containerları başlat
docker-compose -f docker-compose.prod.yml up -d

# 6. Migrations çalıştır
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 7. Static files topla
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 8. Superuser oluştur (opsiyonel)
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# 9. Database optimizasyonları
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c \
  "from django.core.cache import cache; cache.clear()"

# 10. Logları kontrol et
docker-compose -f docker-compose.prod.yml logs -f web
```

---

## 🔍 Post-Deployment Verification

```bash
# API Health Check
curl https://your-domain.com/api/health/

# SSL Certificate Check
curl -I https://your-domain.com

# Docker Containers Status
docker ps

# Service Status
sudo systemctl status ecommerce

# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Database Connection
docker-compose -f docker-compose.prod.yml exec db psql -U ecommerce_user -d ecommerce_prod -c "\dt"
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | `docker-compose logs web` - Nginx config kontrol et |
| Migration Error | `docker-compose exec web python manage.py migrate --fake-initial` |
| Static files Not Found | `docker-compose exec web python manage.py collectstatic --noinput` |
| WebSocket Connection Fails | Redis bağlantısını kontrol et, Nginx config'i doğrula |
| SSL Certificate Error | `sudo certbot renew` |

---

## 📊 Performance Optimization

### **Gunicorn Worker Configuration:**
```
Workers = (2 × CPU_Cores) + 1
Timeout = 120 seconds
Max Requests = 1000
```

### **Database Optimization:**
```sql
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_products_vendor ON products(vendor_id);
CREATE INDEX idx_messages_room ON chat(room_id, created_at DESC);
```

---

## 🔐 Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY rastgele ve güçlü
- [ ] ALLOWED_HOSTS konfigüre edilen domain'lere ayarlandı
- [ ] SSL/HTTPS aktif
- [ ] Database passwords güçlü
- [ ] .env dosyası gitignore'da
- [ ] Firewall sadece 80, 443, SSH portlarını açık tutuyor
- [ ] Regular backups yapılıyor
- [ ] Log monitoring kurulu
- [ ] Rate limiting konfigüre edildi

---

## 📈 Scaling (Gelecek)

- **Load Balancer:** Nginx upstream multiple web containers
- **Database Replication:** PostgreSQL replication
- **CDN:** Cloudflare für static files
- **Cache Warming:** Redis pre-warming
- **Async Tasks:** Celery + RabbitMQ

---

## 🆘 Support Commands

```bash
# Full restart
docker-compose -f docker-compose.prod.yml restart

# View specific logs
docker-compose -f docker-compose.prod.yml logs -f web --tail 100

# Update aplikasi
cd /opt/ecommerce && git pull && docker-compose -f docker-compose.prod.yml build && docker-compose -f docker-compose.prod.yml up -d

# Backup now
bash /opt/ecommerce/backup.sh

# SSH into container
docker-compose -f docker-compose.prod.yml exec web bash
```

---

**Deployment tamamlandı! 🎉**
