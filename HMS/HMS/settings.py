"""
Django settings for HMS project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from dotenv import load_dotenv

load_dotenv()

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-kvg73ir99on-u4xg=d#))cu8bfm*ig8(hvrb8xj$n$h=@5=(bj'
JBKJHKHHLLKHKLJLK
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'DEBUG',
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}



ALLOWED_HOSTS = [ '*']
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000/',
    'https://broadly-lenient-adder.ngrok-free.app',
    'https://adarhotel33.loophole.site',
]

CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# Application definition

import paypalrestsdk
from django.conf import settings


TELEGRAM_BOT_TOKEN='7334373491:AAGp_FxEOXa18iOMTCdNYsNOYkcFBvob3ls'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accountss',
    'room',
    'social_media',
    'crispy_forms',
    'bootstrap4',
    'widget_tweaks',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'oauth2_provider',
    'social_django',
    'admins',
    'gym',
    'Hall',
    'django_countries',
    'paypal.standard.ipn',
    'Spa',
]

import environ

env = environ.Env()
environ.Env.read_env()

# OpenAI API Key
OPENAI_API_KEY = env('OPENAI_API_KEY')



MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Directory where collectstatic will collect static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional directories where Django will search for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accountss.middleware.NoCacheMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'HMS.middleware.TemplateMiddleware',
    
]

SITE_ID = 1




SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

from config import BASE_URL
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Options are 'mandatory', 'optional', or 'none'
ACCOUNT_EMAIL_REQUIRED = True

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = f'{os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY1")}'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET =f'{os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET1")}'
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SOCIAL_AUTH_LOGIN_ERROR_URL = 'login'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False



ROOT_URLCONF = 'HMS.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'HMS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'HMS',
         'USER': 'postgres',
         'PASSWORD': '2112',
         'HOST': 'localhost',
         'PORT': '5432',
     }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'accountss.Custom_user'


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'social_core.backends.google.GoogleOAuth2',
)

RUN_TELEGRAM_BOT = True


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = 'hueymail.backends.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # SMTP server host
EMAIL_PORT = 587  # SMTP server port (587 for TLS, 465 for SSL)
EMAIL_USE_TLS = True  # True for TLS, False for SSL
EMAIL_HOST_USER = f'{os.getenv("EMAIL_HOST_USER1")}'  
EMAIL_HOST_PASSWORD = f'{os.getenv("EMAIL_HOST_PASSWORD1")}'  
EMAIL_USE_SSL = False  # Set to True if using SSL
DEFAULT_FROM_EMAIL = f'{os.getenv("EMAIL_HOST_USER1")}'  # Default sender email address

