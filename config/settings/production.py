from .base import *

DEBUG = os.environ.get('DEBUG', 'False').lower() in {'1', 'true', 'yes', 'on'}
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ.get('DB_NAME', os.environ.get('POSTGRES_DB', 'ecommerce')),
		'USER': os.environ.get('DB_USER', os.environ.get('POSTGRES_USER', 'postgres')),
		'PASSWORD': os.environ.get('DB_PASSWORD', os.environ.get('POSTGRES_PASSWORD', '1234')),
		'HOST': os.environ.get('DB_HOST', os.environ.get('POSTGRES_HOST', 'db')),
		'PORT': os.environ.get('DB_PORT', os.environ.get('POSTGRES_PORT', '5432')),
	}
}