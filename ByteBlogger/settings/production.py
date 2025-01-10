import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if needed)
load_dotenv()

# Get ALLOWED_HOSTS from environment variables
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database configuration for production using environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'your_db_name'),
        'USER': os.getenv('DB_USER', 'your_db_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'your_db_password'),
        'HOST': os.getenv('DB_HOST', 'your_db_host'),
        'PORT': os.getenv('DB_PORT', 'your_db_port'),
    }
}

print('hello from production')
