from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-p-a-$+fet#iu^-e)s^z^d^vkv=(u7-howm07h1si+06%sikd0h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# # Set the 'SECURE_SSL_REDIRECT' setting to True to force HTTPS
# SECURE_SSL_REDIRECT = True
# ALLOWED_HOSTS = ["192.168.3.73"]
ALLOWED_HOSTS = ["*","127.0.0.1","core.flxdevpanel.com","www.core.flxdevpanel.com",'app.flxdevpanel.com','www.app.flxdevpanel.com']

AUTHENTICATION_BACKENDS = [
    'accounts.custom_authentication.UsernameBackend',  # Replace 'your_app_name' with the actual name of your app
    'django.contrib.auth.backends.ModelBackend',  # Keep the default ModelBackend
    "allauth.account.auth_backends.AuthenticationBackend",
]   
SITE_ID = 1

CSRF_TRUSTED_ORIGINS = ['https://app.flxdevpanel.com']
# Application definition
USE_X_FORWARDED_HOST = True
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'dj_rest_auth',
    'django.contrib.sites',

    'django_countries',
    'fcm_django',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework.authtoken',
    'allauth.socialaccount.providers.apple',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth.registration',
    # Project Apps:
    'flibbo_base',
    'notification',
    'chat_openai',
    'following_system',
    'accounts',
    'tokens',
    'category',
    'posts',
    'marketplace',
    'wallet',
    'activity',
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
    'accounts.middleware.CheckHostMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'flibbo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# CORS_ALLOWED_ORIGINS = [
#     'flxdevpanel.com',
# ]     
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

WSGI_APPLICATION = 'flibbo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'flxdev_flibbo_db',
        'USER': 'flxdev_flibbo_db_user',
        'PASSWORD': '#@0AHirbodaflaki13831383',
        'HOST': '127.0.0.1',  # Change this if your database is on a different host
        'PORT': '5432',           # Leave this empty to use the default PostgreSQL port (5432)
    }
}






# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
import os

STATIC_URL = '/static/'
STATIC_ROOT = '../flibbo/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '../flibbo/media/'
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "accounts.CustomUser"

from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Add this line
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    # Other DRF settings...
}


from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365 * 100),  # 100 years
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=365 * 100),  # 100 years
    'SLIDING_TOKEN_LIFETIME': timedelta(days=365 * 100),  # 100 years
    'SLIDING_TOKEN_REFRESH_LIFETIME_GRACE_PERIOD': timedelta(days=0),
    'SLIDING_TOKEN_REFRESH_EACH_TIME': True,
    'SLIDING_TOKEN_LIFETIME_GRACE_PERIOD': timedelta(minutes=15),
}




# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.flxdevpanel.com'  # Google's SMTP server
# EMAIL_PORT = 465  # Use port 587 for TLS
# EMAIL_USE_TLS = True  # Use TLS for secure communication
# EMAIL_USE_SSL = False  # Set this to False when using TLS
# EMAIL_HOST_USER = 'noreply@flxdevpanel.com'  # Your Gmail email address
# EMAIL_HOST_PASSWORD = '0AFlibbo3002617425@'  # Your Gmail email password
# DEFAULT_FROM_EMAIL = 'noreply@flxdevpanel.com'  # The default "from" email address


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Google's SMTP server
EMAIL_PORT = 587  # Use port 587 for TLS
EMAIL_USE_TLS = True  # Use TLS for secure communication
EMAIL_USE_SSL = False  # Set this to False when using TLS
EMAIL_HOST_USER = 'flibboapp.info@gmail.com'  # Your Gmail email address
EMAIL_HOST_PASSWORD = 'saadvedokxaiksyb'  # Your Gmail email password
DEFAULT_FROM_EMAIL = 'flibboapp.info@gmail.com'  # The default "from" email address




from firebase_admin import initialize_app

# FIREBASE_APP = initialize_app()
FIREBASE_APP_POSTS = initialize_app(name="posts")
FIREBASE_APP_NOTIFICATION = initialize_app(name="notification")

# To learn more, visit the docs here:
# https://cloud.google.com/docs/authentication/getting-started>

FCM_DJANGO_SETTINGS = {
     # an instance of firebase_admin.App to be used as default for all fcm-django requests
     # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": FIREBASE_APP_NOTIFICATION,
    "FCM_SERVER_KEY": os.getenv("FCM_SERVER_KEY"),
     # default: _('FCM Django')
    "APP_VERBOSE_NAME": "[string for AppConfig's verbose_name]",
     # true if you want to have only one active device per registered user at a time
     # default: False
    # "ONE_DEVICE_PER_USER": True/False,
     # devices to which notifications cannot be sent,
     # are deleted upon receiving error response from FCM
     # default: False
    # "DELETE_INACTIVE_DEVICES": True/False,
}



SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '518092834966-avk6omgdn1spp3162joo3rdtpn5p97fr.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    "apple": {
        "APP": {
            # Your service identifier.
            "client_id": "com.flibbo.app",

            # The Key ID (visible in the "View Key Details" page).
            "secret": "97KZ9297PC",

             # Member ID/App ID Prefix -- you can find it below your name
             # at the top right corner of the page, or it’s your App ID
             # Prefix in your App ID.
            "key": "DX759ANS8K",

            "settings": {
                # The certificate you downloaded when generating the key.
                "certificate_key": """-----BEGIN PRIVATE KEY-----
                MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgkMu+ZswmcQW7dWF2
                NHfpcwipuWZxAmUq3rU7nHTgNPugCgYIKoZIzj0DAQehRANCAAS+j9yoV7IfzIq8
                Tk6wOHc0rW9aX7cJbCAnNgeQjrVTKLp7+KZ620ycCvddwvxFKEaPA33jYym+vEKm
                GOPgtAtO
                -----END PRIVATE KEY-----
                """
                }
            },
        }
}

