from .base import *
import os

# Quick-start development settings
DEBUG = True

SECRET_KEY = 'django-insecure-*v##h_vex_ri)l+s7m$wg#0jzecxk5#&xot8w(rp^21t*b%fqa'

ALLOWED_HOSTS = []

# Database configuration for development (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'  # Convert to boolean
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')