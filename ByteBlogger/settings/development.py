from .base import *

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
