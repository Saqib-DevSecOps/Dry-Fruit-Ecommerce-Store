import datetime
import os
from pathlib import Path
import environ

""" APPLICATION CONFIGURATIONS """

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, True)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env('DEBUG')
MAINTENANCE = env('MAINTENANCE')
DOMAIN = env('DOMAIN')
PROTOCOL = env('PROTOCOL')
BASE_URL = f"{PROTOCOL}://{DOMAIN}"
ALLOWED_HOSTS = str(env('ALLOWED_HOSTS')).split(',')
CSRF_TRUSTED_ORIGINS = [f'{PROTOCOL}://{host}' for host in ALLOWED_HOSTS]
ENVIRONMENT = env('ENVIRONMENT')
ROOT_URLCONF = 'core.urls'
AUTH_USER_MODEL = 'accounts.User'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
LOGOUT_URL = '/accounts/logout/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/cross-auth/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECRET_KEY = env('SECRET_KEY', default='default_secret_key')
GOOGLE_CALLBACK_ADDRESS = f"{BASE_URL}{env('GOOGLE_CALLBACK_URL')}"
APPLE_CALLBACK_ADDRESS = ''

SITE_ID = 1

INSTALLED_APPS = [
    'jazzmin',

    # DJANGO APPS
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # STARTER APPS
    'crispy_forms',
    "crispy_bootstrap5",
    'django_filters',
    'widget_tweaks',
    'tinymce',

    # WEB APPS
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    # REST APPS
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'drf_yasg',

    # YOUR APPS
    'src.website.apps.WebsiteConfig',
    'src.api.apps.ApiConfig',
    'src.accounts.apps.AccountsConfig',
    'src.administration.admins.apps.AdministrationAdminConfig',
    'src.administration.client.apps.ClientConfig',
    'src.apps.stripe.apps.StripeConfig',
    'src.apps.whisper.apps.WhisperConfig',
    'src.apps.razorpay.apps.RazorpayConfig',
    'src.apps.shipment',
]

MIDDLEWARE = [
    # DJANGO MIDDLEWARES
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # YOUR MIDDLEWARES
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],
}

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
                'src.website.context_processor.get_total_counts_context_processor',

            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

if ENVIRONMENT == 'server':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASS'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

""" INTERNATIONALIZATION --------------------------------------------------------------------------------"""
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

""" EMAIL CONFIGURATION --------------------------------------------------------------------------------"""

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "donald.duck0762@gmail.com"
EMAIL_HOST_PASSWORD = "dszdssspgghirkim"
EMAIL_PORT = "587"
DEFAULT_FROM_EMAIL = 'support@exarth.com'

""" RESIZER IMAGE --------------------------------------------------------------------------------"""
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'assets'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

""" RESIZER IMAGE --------------------------------------------------------------------------------"""
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {
    'JPEG': ".jpg",
    'PNG': ".png",
    'GIF': ".gif"
}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

""" ALL-AUTH SETUP --------------------------------------------------------------------------------"""

ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

RAZORPAY_API_KEY = env("RAZORPAY_API_KEY")
RAZORPAY_API_SECRET = env("RAZORPAY_API_SECRET")
SHIPROCKET_EMAIL = env("SHIPROCKET_EMAIL")
SHIPROCKET_PASSWORD = env("SHIPROCKET_PASSWORD")
