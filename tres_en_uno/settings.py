"""
Django settings for tres_en_uno project.
VERSIÓN CORREGIDA PARA PRODUCCIÓN CON RESEND API
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECURITY WARNING
# ==============================================================================

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS
ALLOWED_HOSTS = []

# Agregar hosts desde variable de entorno
env_hosts = config('ALLOWED_HOSTS', default='').strip()
if env_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in env_hosts.split(',') if host.strip()])

# Dominios fijos
ALLOWED_HOSTS.extend([
    'tresenunocultivos.cl',
    'www.tresenunocultivos.cl',
])

# Railway dynamic hosts
if 'RAILWAY_STATIC_URL' in os.environ:
    railway_url = os.environ.get('RAILWAY_STATIC_URL', '')
    railway_domain = railway_url.replace('https://', '').replace('http://', '').strip('/')
    if railway_domain and railway_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_domain)

if 'RAILWAY_PUBLIC_DOMAIN' in os.environ:
    railway_domain = os.environ['RAILWAY_PUBLIC_DOMAIN'].strip()
    if railway_domain and railway_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_domain)

# Fallback para desarrollo local
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ==============================================================================
# INSTALLED APPS
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    
    # Local apps
    'miapp',
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tres_en_uno.urls'

# ==============================================================================
# TEMPLATES
# ==============================================================================

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

WSGI_APPLICATION = 'tres_en_uno.wsgi.application'

# ==============================================================================
# DATABASE - CORREGIDO PARA RAILWAY
# ==============================================================================

DATABASE_URL_CONFIG = config('DATABASE_URL', default=None)

if DATABASE_URL_CONFIG:
    # Producción (Railway) - usar DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL_CONFIG,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=False
        )
    }
else:
    # Desarrollo local - usar variables individuales
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='tresenuno_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
        }
    }

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC FILES
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

# Agregar directorio static si existe
static_dir = BASE_DIR / 'static'
if static_dir.exists():
    STATICFILES_DIRS.append(static_dir)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise configuración
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_MANIFEST_STRICT = False

# Storage según entorno
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================================================================
# MEDIA FILES
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# ==============================================================================
# AUTHENTICATION
# ==============================================================================

AUTH_USER_MODEL = 'miapp.Cliente'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/perfil/'
LOGOUT_REDIRECT_URL = '/'

# ==============================================================================
# REST FRAMEWORK
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
}

# ==============================================================================
# JWT CONFIGURATION
# ==============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ==============================================================================
# EMAIL CONFIGURATION - SOLO PARA RESEND API
# ==============================================================================

# Solo necesitamos estas variables para usar la API de Resend en views.py
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # API key de Resend
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='onboarding@resend.dev')

# ==============================================================================
# SITE CONFIGURATION
# ==============================================================================

# Determinar SITE_URL según el entorno
if 'RAILWAY_STATIC_URL' in os.environ:
    SITE_URL = os.environ.get('RAILWAY_STATIC_URL').rstrip('/')
elif not DEBUG:
    SITE_URL = config('SITE_URL', default='https://tresenunocultivos.cl')
else:
    SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')

# ==============================================================================
# SESSION CONFIGURATION
# ==============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# En producción, usar cookies seguras
if not DEBUG:
    SESSION_COOKIE_SECURE = True

# ==============================================================================
# CSRF CONFIGURATION
# ==============================================================================

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        'https://tresenunocultivos.cl',
        'https://www.tresenunocultivos.cl',
        'https://*.railway.app',
        'https://*.up.railway.app',
    ]
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]

# ==============================================================================
# SECURITY SETTINGS (PRODUCCIÓN)
# ==============================================================================

if not DEBUG:
    # HTTPS
    SECURE_SSL_REDIRECT = False  # Railway maneja el redirect
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Otras configuraciones de seguridad
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_BROWSER_XSS_FILTER = True

# ==============================================================================
# LOGGING CONFIGURATION (CRÍTICO PARA EL CHECKOUT)
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django_errors.log',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'miapp': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================================================
# ADMINS (reciben correos de errores críticos)
# ==============================================================================

ADMINS = [
    ('Admin Tres en Uno', 'ventas.tresenuno@gmail.com'),
]

MANAGERS = ADMINS

# ==============================================================================
# OTHER SETTINGS
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# DEVELOPMENT OVERRIDES
# ==============================================================================

if DEBUG:
    # Logging más verboso en desarrollo
    LOGGING['root']['level'] = 'DEBUG'
    LOGGING['loggers']['miapp']['level'] = 'DEBUG'