# Production Settings Configuration Guide

Bu dosya, `config/settings/production.py`'nde yapılması gereken ayarlamaları açıklar.

## ❗ UYARI

**Bu dosyayı local development'ta DEĞİŞTİRME!**  
Sadece production server'da, deployment sırasında kullan.

---

## ✅ Production Settings Checklist

### 1. Django Security

```python
# config/settings/production.py

# DEBUG MUTLAKA FALSE olmalı
DEBUG = False

# SECRET_KEY güçlü ve random olmalı
# ASLA default değeri kullanma!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set!")

# ALLOWED_HOSTS tam tanımlanmalı
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS[0] == '':
    raise ValueError("ALLOWED_HOSTS environment variable not set!")

# SSL/TLS Ayarları
SECURE_SSL_REDIRECT = True  # HTTP → HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session & CSRF Security
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # JavaScript'ten erişilemez
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Browser Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),  # Unsafe-inline sadece test'te
    'style-src': ("'self'", "'unsafe-inline'"),
}

X_FRAME_OPTIONS = 'DENY'  # Clickjacking koruması
```

### 2. Database Configuration

```python
# Production PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ecommerce_prod'),
        'USER': os.environ.get('DB_USER', 'ecommerce_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        
        # Performance Settings
        'CONN_MAX_AGE': 600,  # Connection pooling
        'ATOMIC_REQUESTS': True,  # Transaction safety
        
        # SSL Configuration (opsiyonel)
        # 'OPTIONS': {
        #     'sslmode': 'require',
        # }
    }
}

# Connection Validation
DATABASES['default']['CONN_HEALTH_CHECKS'] = True
```

### 3. Redis / Cache Configuration

```python
# Redis Connection
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_CHANNEL_DB = os.environ.get('REDIS_CHANNEL_DB', '0')
REDIS_CACHE_DB = os.environ.get('REDIS_CACHE_DB', '1')
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}"

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}

# Session'u Redis'te sakla
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Channel Layers (WebSockets)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [f'{REDIS_URL}/{REDIS_CHANNEL_DB}'],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}
```

### 4. Static & Media Files

```python
# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Optional: S3 Storage (AWS)
# if os.environ.get('USE_S3'):
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
#     AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
#     AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
#     AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
#     STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
```

### 5. Email Configuration

```python
# Email Backend Production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Test Email Configuration
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    pass  # Configuration is valid
else:
    print("⚠️  Email not configured - transactional emails won't be sent")
```

### 6. Logging Configuration

```python
# Comprehensive Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        }
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'payments': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'services': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'chat': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

# Create logs directory if it doesn't exist
import os as os_module
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os_module.path.exists(LOGS_DIR):
    os_module.makedirs(LOGS_DIR, exist_ok=True)
```

### 7. REST Framework Configuration

```python
REST_FRAMEWORK = {
    # Sadece JSON render et (production'da)
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',  # Disable in production
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    
    # Filtering & Searching
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Permissions (default: authenticated)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Throttling (Rate Limiting)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    
    # Exception Handling
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
    
    # Metadata
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JTI_CLAIM': 'jti',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',

    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

### 8. CORS Configuration

```python
from corsheaders.defaults import default_headers

# Frontend domain'lerini ekle
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# In development only:
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
    ])

CORS_ALLOW_HEADERS = list(default_headers) + [
    'authorization',
    'content-type',
]

CORS_ALLOW_CREDENTIALS = True
CORS_MAX_AGE = 3600
```

### 9. Middleware Configuration

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise for static files (alternative to Nginx)
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 10. Admin Configuration

```python
# Güvenlik için admin path'ini değiştir
# ADMIN_URL = 'admin-secret-path/'

# Admin site customization
from django.contrib import admin

admin.site.site_header = "E-Commerce Admin"
admin.site.site_title = "E-Commerce Admin Portal"
admin.site.index_title = "Welcome to E-Commerce Management"
```

---

## ⚙️ Environment Variables Full List

**.env dosyasında şu değişkenleri ayarla:**

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=domain.com,www.domain.com,ip.address

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_prod
DB_USER=ecommerce_user
DB_PASSWORD=strong_password_here
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

# CORS
CORS_ALLOWED_ORIGINS=https://frontend.domain.com,https://www.frontend.domain.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password
DEFAULT_FROM_EMAIL=noreply@domain.com

# Logging
LOG_LEVEL=INFO

# Optional: Third-party services
# SENTRY_DSN=xxx
# STRIPE_SECRET_KEY=xxx
# AWS_ACCESS_KEY_ID=xxx
```

---

## 🔍 Production Settings Validation

Production'a geçmeden önce validate et:

```bash
# Django check
python manage.py check --deploy

# Environment variables
python manage.py shell -c "\
from django.conf import settings;\
print('DEBUG:', settings.DEBUG);\
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS);\
print('DATABASES:', settings.DATABASES);\
"

# Migrations applied
python manage.py showmigrations

# Collectstatic
python manage.py collectstatic --dry-run
```

---

## 📋 Production Settings Comparison

| Setting | Local | Production |
|---------|-------|------------|
| DEBUG | True | False ✅ |
| ALLOWED_HOSTS | ['*'] | ['domain.com'] ✅ |
| SECURE_SSL_REDIRECT | False | True ✅ |
| SESSION_COOKIE_SECURE | False | True ✅ |
| DATABASES | SQLite | PostgreSQL ✅ |
| EMAIL_BACKEND | Console | SMTP ✅ |
| CACHE | Dummy | Redis ✅ |

---

## ⚠️ Common Mistakes

❌ **Yapma:**
- DEBUG = True ile production'a git
- SECRET_KEY'i commit et
- Default database password kullan
- Localhost'u ALLOWED_HOSTS'a ekle
- HTTP bağlantısına izin ver
- Email'i debug mode'da test et

✅ **Yap:**
- DEBUG = False kodu
- Strong random SECRET_KEY oluştur
- Strong unique passwords kullan
- Production domain'lerini ekle
- HTTPS enforcelamayı aç
- Email production'da test et

---

**Son Kontrol:** Tüm production settings doğru ayarlandı mı? Deployment'a başla! 🚀
