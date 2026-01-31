from pathlib import Path
from dotenv import load_dotenv
import os

#---------------------------------------------
load_dotenv()
#---------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

#---------------------------------------------
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_spectacular',
    'corsheaders',
    'rest_framework',
    'django_filters',
    'post',
]
#---------------------------------------------
MIDDLEWARE = [
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
#---------------------------------------------
ROOT_URLCONF = 'config.urls'
#---------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
#---------------------------------------------
WSGI_APPLICATION = 'config.wsgi.application'
#---------------------------------------------
# Database
DATABASES = {
    'default': {
        'NAME': os.getenv("POSTGRES_DB"),
        'USER': os.getenv("POSTGRES_USER"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD"),
        'HOST': os.getenv("POSTGRES_HOST"),
        'PORT': os.getenv("POSTGRES_PORT"),
    }
}
#---------------------------------------------
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# REST Framework Configuration
# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
#---------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
#---------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#---------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#SWAGGER
SPECTACULAR_SETTINGS = {
    'TITLE': 'Chat API Documentation',
    'DESCRIPTION': 'API documentation for Chat',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
    },
    # Disable automatic tag generation based on URL prefixes
    'COMPONENT_SPLIT_REQUEST': True,
    'ENUM_NAME_OVERRIDES': {},
    'TAG_SORTING': 'alpha',  # Sort tags alphabetically
}

ENVIRONMENT = os.getenv("ENVIRONMENT")
# Allowed hosts
if ENVIRONMENT == "development":

    print(ENVIRONMENT)
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    ALLOWED_EXPORT_IPS = os.environ.get("ALLOWED_EXPORT_HOSTS", default='').split(",")
    ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    ALLOWED_USER = os.environ.get("ALLOWED_USER", default='')
    SECRET_KEY_API = os.getenv("SECRET_KEY_API", "fallback-secret-key")
    CORS_ALLOW_ALL_ORIGINS = False  # Explicitly disable
    CORS_ALLOWED_ORIGINS = [

    ]
    CSRF_TRUSTED_ORIGINS = [

    ]