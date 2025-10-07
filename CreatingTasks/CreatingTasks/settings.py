import os
from pathlib import Path
from datetime import timedelta

# Базовые пути для проекта CreatingTasks
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'creating-tasks-dev-secret-key-2024')
PROJECT_NAME = "CreatingTasks"
DEBUG = True

ROOT_URLCONF = 'CreatingTasks.urls'
WSGI_APPLICATION = 'CreatingTasks.wsgi.application'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Настройки приложений с префиксом CreatingTasks
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'corsheaders',
    'allauth',
    'allauth.account',

    # CreatingTasks apps
    'apps.users',
    'apps.tasks',
    'apps.notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Создайте папку templates если её нет
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database configuration for CreatingTasks
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ДОБАВЬТЕ в начало файла (после импортов):
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis для CreatingTasks
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# WebSocket routing для CreatingTasks
ASGI_APPLICATION = 'CreatingTasks.asgi.application'

# Channels configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
        },
    },
}

# Celery для CreatingTasks
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# CreatingTasks API Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Static files для CreatingTasks
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CreatingTasks Security
CSRF_COOKIE_NAME = f"{PROJECT_NAME.lower()}_csrftoken"
SESSION_COOKIE_NAME = f"{PROJECT_NAME.lower()}_sessionid"

# Telegram Bot для CreatingTasks
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', 'CreatingTasksBot')

os.makedirs(BASE_DIR / 'templates', exist_ok=True)
os.makedirs(BASE_DIR / 'static', exist_ok=True)

AUTH_USER_MODEL = 'users.User'