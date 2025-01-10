from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Common apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',  # Django REST Framework
    'django.contrib.staticfiles',  # Static files
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection (can be removed for API-only)
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration
ROOT_URLCONF = 'ByteBlogger.urls'

# Database configuration (default to SQLite, but this should be overridden in production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation (can be omitted or modified if needed)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Localization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings (can be customized for your project)
REST_FRAMEWORK = {
    # Default permission classes (can be adjusted depending on your requirements)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Require authentication for all views
    ],
    # Default authentication classes
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # Token-based authentication
    ],
    # Pagination settings (if needed for large sets of data)
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE':
    10,
    # Enable browsable API (can be disabled for production)
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # JSON response (for API)
    ],
    # Enable API throttling if necessary
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',  # Rate limiting for anonymous users
        'rest_framework.throttling.UserRateThrottle',  # Rate limiting for authenticated users
    ],
    'DEFAULT_THROTTLE_RATE':
    '100/day',  # Set throttling rate (can be customized)
    # Enable versioning of the API
    'DEFAULT_VERSIONING_CLASS':
    'rest_framework.versioning.AcceptHeaderVersioning',  # Enable versioning via Accept header
}

# CORS (Cross-Origin Resource Sharing) settings (if needed for your API)
# Allow your frontend to make requests to this API server (modify as needed)
CORS_ORIGIN_ALLOW_ALL = True  # Allow all origins (you can restrict this in production)

# Session and CSRF handling for API (optional, depending on your setup)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Use cache-backed sessions for API
CSRF_COOKIE_HTTPONLY = True  # Enable CSRF cookie with HTTP-only flag for security
