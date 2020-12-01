"""
Django settings for this project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from datetime import timedelta
import os

from corsheaders.defaults import default_headers
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'override_me_in_prod'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

BUILD_VERSION = os.getenv("BUILD_VERSION", "")

# Semantic versioning + build version
VERSION = f"0.0.0_{BUILD_VERSION}"

AUTH_USER_MODEL = 'users.User'

# Returns user even if it's not active, lets do handle it manually
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

APP_HOST = os.getenv('APP_HOST', 'http://localhost:8000/')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'solo',
    "watchman",
    'ckeditor',
    'ckeditor_uploader',

    'tabbed_admin',

    # local
    # https://docs.djangoproject.com/en/3.1/ref/applications/#django.apps.AppConfig.ready
    'apps.home.apps.HomeConfig',
    'apps.api.apps.ApiConfig',
    'apps.translations.apps.TranslationsConfig',
    'apps.users.apps.UsersConfig',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = list(default_headers)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "apps/home/templates")],
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

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if os.getenv('DATABASE_URL'):
    # For heroku
    DATABASES = dj_database_url.config(os.getenv('DATABASE_URL'), conn_max_age=os.getenv('CONN_MAX_AGE', 600))
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DB_NAME', 'django'),
            'USER': os.getenv('DB_USER', 'django'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'django'),
            'PORT': os.getenv('DB_PORT', 9432),
            'CONN_MAX_AGE': os.getenv('CONN_MAX_AGE', 600),
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'custom': {
            'format': '%(levelname)s %(asctime)s %(process)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'custom'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_LANGUAGE = 'lt'
TRANSLATIONS_BASE_LANGUAGE = ('lt', 'Lithuanian')
MANIFEST_JS_MAX_AGE = 0

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static/'))

# user uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, 'media/'))

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.CustomPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.utils.authentication.JWTTokenUserAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'COERCE_DECIMAL_TO_STRING': False
}

# user uploads
FILE_UPLOAD_PERMISSIONS = 0o644
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False

CKEDITOR_CONFIGS = {
    'default': {
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
        'entities': False,
        'toolbar': [
            {'name': 'clipboard', 'groups': ['clipboard', 'undo'],
             'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'groups': ['find', 'selection'], 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup'],
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'CopyFormatting',
                       'RemoveFormat']},
            {'name': 'paragraph', 'groups': ['list', 'indent', 'blocks', 'align', 'bidi'],
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-', 'JustifyLeft',
                       'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'Source']},
            '/',
            {'name': 'styles', 'items': ['Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'others', 'items': ['-']}
        ]
    }
}

# Email settings
DEFAULT_FROM_EMAIL = ''
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '<email-host>'
EMAIL_HOST_PASSWORD = '<email-psw>'
EMAIL_PORT = 587

# Celery settings
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

VERIFICATION_BASE_URL = '{}verify/{}'
RESET_PASSWORD_BASE_URL = '{}reset-password/{}'
PASSWORD_TOKEN_EXPIRATION_PERIOD = 12  # in hours

TABBED_ADMIN_USE_JQUERY_UI = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer', 'Token', 'JWT'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
