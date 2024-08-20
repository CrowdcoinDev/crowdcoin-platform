import os
import uuid
from logentries import LogentriesHandler
import dj_database_url
import environ
from django.core.management.utils import get_random_secret_key

uuid._uuid_generate_random = None

def str_to_bool(s):
    return s.lower() in ['true', '1', 't', 'yes', 'y']


# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())

DEBUG = bool(env('DJANGO_DEBUG',default=False))

CROWDCOIN_ENV = os.environ.get('CROWDCOIN_ENV','DEVELOPMENT')

PRODUCTION = True if CROWDCOIN_ENV == 'PRODUCTION' else False

CROWDCOIN_USSD_STRING = "*120*912*87*87#"

ALLOWED_HOSTS = ['*'] if DEBUG else ['localhost', '127.0.0.1', '.fly.dev', '.crowdcoin.co.za']
CSRF_TRUSTED_ORIGINS = ['https://*.fly.dev', 'https://*.crowdcoin.co.za']

CELERY_ACCEPT_CONTENT = ['json']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'website',
    'django.contrib.sites',
    'tastypie',
    'whatsapp_bot',
    'oauth2_provider',
    'corsheaders',
    'MiUSSD',
    'kazang',
]

SITE_ID = 1

AUTH_USER_MODEL = 'website.User'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
]

ROOT_URLCONF = 'crowdcoincoza.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'crowdcoincoza.wsgi.application'

# Database
DATABASE_URL = env('DATABASE_URL', default='sqlite:///db.sqlite3')
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'

# Internationalization
LANGUAGE_CODE = 'en-za'
TIME_ZONE = 'Africa/Johannesburg'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static_files")]
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

TASTYPIE_ALLOW_MISSING_SLASH = True
X_FRAME_OPTIONS = 'DENY'  # Adjusted for security

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'crowdcoin-django.log',
            'formatter': 'verbose'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
        },
        'website': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'xhtml2pdf': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'celery.task': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'whatsapp_bot': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'MiUSSD': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'kazang': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        }
    }
}

SESSION_SAVE_EVERY_REQUEST = True
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'

# Email settings
EMAIL_USE_TLS = bool(os.environ.get('EMAIL_USE_TLS'))
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Freshdesk settings
FRESHDESK_URL = os.environ.get('FRESHDESK_URL', 'crowdcoin.freshdesk.com/')
FRESHDESK_KEY = os.environ.get('FRESHDESK_KEY')

SUPPORTED_NETWORKS = ["MTN"]

# Crowdcoin fees
VOUCHER_SENDING_FEE = 0
VOUCHER_RECIEVING_FEE = 0

# Panacea settings
PANACEA_USER = os.environ.get('PANACEA_USER')
PANACEA_PASSWORD = os.environ.get('PANACEA_PASSWORD')

# TIM settings
TIM_CERT = os.environ.get('TIM_CERT')
TIM_KEY = os.environ.get('TIM_KEY')

# Kazang settings
KAZANG_USERNAME = os.environ.get('KAZANG_USERNAME')
KAZANG_PASSWORD = os.environ.get('KAZANG_PASSWORD')
KAZANG_DEBUG = str_to_bool(os.environ.get('KAZANG_DEBUG', 'False'))

# Whatsapp settings
WEBHOOK_VERIFY_TOKEN = os.environ.get('WEBHOOK_VERIFY_TOKEN', None)
GRAPH_API_TOKEN = os.environ.get('GRAPH_API_TOKEN', None)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
# FLOW_PRIVATE_KEY = os.environ.get('FLOW_PRIVATE_KEY', 'whatsapp_bot/configs/private.pem')
FLOW_PASSPHRASE = os.environ.get('FLOW_PASSPHRASE', 'passphrase')


CORS_ORIGIN_ALLOW_ALL = True

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

# Django OAuth Toolkit settings
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 600,
    # 'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore',
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'}
}

print('DEBUG:',DEBUG)
print('PRODUCTION:',PRODUCTION)