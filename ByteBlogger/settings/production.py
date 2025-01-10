from .base import *

DEBUG = False

SECRET_KEY = 'your-secure-production-secret-key'

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database configuration for production (e.g., PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'your_db_host',
        'PORT': 'your_db_port',
    }
}

STATIC_URL = '/static/'

