
from celery.schedules import crontab
from pathlib import Path, os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-any&$e=8_%j$4u1aw@%b_uo!+0x(88%aj0h!1&m4pqic(cjv(l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'stakeholder.apps.StakeholderConfig',
    'user',
    'hoteldetails',

    'crispy_forms',
    'crispy_bootstrap5',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_celery_beat'
]


# or 'bootstrap5' if you're using Bootstrap 5
CRISPY_TEMPLATE_PACK = 'bootstrap5'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'FeatherFarmSoloutions.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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


WSGI_APPLICATION = 'FeatherFarmSoloutions.wsgi.application'

#dpg-csl5vh56l47c73e6h07g-a
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'featherfarm',
#         'USER': 'root',
#         'PASSWORD': '',
#         'HOST': 'localhost',  # Set to your database host
#         'PORT': '3306',       # Default MySQL port
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         }
#     }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'featherfarm_db',
#         'USER': 'featherfarm_db_user',
#         'PASSWORD': 'ZzQ5IA8eVibOFi0uasnmXmuAdYEy3uLF',
#         'HOST': 'dpg-csl5vh56l47c73e6h07g-a',  # Set to your database host
#         'PORT': '5432',       # Default MySQL port
#        "default": dj_database_url.parse("postgresql://featherfarm_db_user:ZzQ5IA8eVibOFi0uasnmXmuAdYEy3uLF@dpg-csl5vh56l47c73e6h07g-a.oregon-postgres.render.com/featherfarm_db") 
#         }
#     }

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://featherfarm_db_user:ZzQ5IA8eVibOFi0uasnmXmuAdYEy3uLF@dpg-csl5vh56l47c73e6h07g-a.oregon-postgres.render.com/featherfarm_db'
    )
}




SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
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

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR/"static"
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'nimyathomas3@gmail.com'
EMAIL_HOST_PASSWORD = 'isfa lred wfxt ujws'


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'user.backends.EmailBackend',
    'allauth.account.auth_backends.AuthenticationBackend',

)

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = True

CLIENT_ID = "993464726518-dlvqdjptpid7jmdsubuivfhe36ncc0at.apps.googleusercontent.com"
part1 = "GOCSPX"
part2 = "ahmTIfCelacuDxLKeiZ5JiX"
part3 = "Y1rx"
my_string = f"{part1}-{part2}-{part3}"


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',
        },
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': CLIENT_ID,
            'secret': my_string,
            'key': ''
        }
    }
}

SITE_ID = 2

LOGIN_REDIRECT_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'

AUTH_USER_MODEL = 'user.User'
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis URL
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = 'Asia/Kolkata'  # Use your timezone

# settings.py


CELERY_BEAT_SCHEDULE = {
    'send-expiry-alerts': {
        'task': 'user.tasks.send_expiry_alerts',
        'schedule': crontab(hour=23, minute=7),  # Daily at 3:03 PM
    },
    'deactivate-expired-users-every-day': {
        'task': 'user.tasks.deactivate_expired_users',
        'schedule': 86400.0,  # Run once every 24 hours (86400 seconds)
    },
}
