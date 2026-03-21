from .base import *

DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ.get('POSTGRES_DB', 'ecommerce'),
		'USER': os.environ.get('POSTGRES_USER', 'ecommerce'),
		'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'ecommerce'),
		'HOST': os.environ.get('POSTGRES_HOST', 'db'),
		'PORT': os.environ.get('POSTGRES_PORT', '5432'),
	}
}