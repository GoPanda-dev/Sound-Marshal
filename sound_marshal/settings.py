import os
from dotenv import load_dotenv
from pathlib import Path
import dj_database_url

load_dotenv()  # Load environment variables from .env file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.getenv('PRODUCTION') == 'TRUE':
    # Production settings

    # Azure Storage settings
    AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
    AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
    AZURE_STATIC_CONTAINER = 'static'
    AZURE_MEDIA_CONTAINER = 'media'
    AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/'
    STATICFILES_STORAGE = 'storages.backends.azure_storage.AzureStorage'

    # Media files (Uploaded by users)
    MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_MEDIA_CONTAINER}/'
    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
else:
    # Local development settings

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # Media files (Uploaded by users)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
SECRET_KEY = 'django-insecure-xilcnhd37a3!jg(xa-b7)qk+yzutg&iv5&30+%4d62f8bhok4('
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.61', 'soundmarshal.azurewebsites.net', 'www.soundmarshal.azurewebsites.net', 'dev.soundly.in']

CSRF_TRUSTED_ORIGINS = [
    'https://soundmarshal.azurewebsites.net',
    'https://dev.soundly.in',
]

INSTALLED_APPS = [
    'core',
    'django.contrib.sites',
    'storages',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.spotify',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'core.middleware.ProfileCreationMiddleware',
    'core.middleware.ThemeMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True

ROOT_URLCONF = 'sound_marshal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # This line ensures Django looks in the 'templates' directory at the project root
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'context_processors.media_url',
            ],
        },
    },
]


WSGI_APPLICATION = 'sound_marshal.wsgi.application'

print("Environment Variable PRODUCTION:", os.getenv('PRODUCTION'))

if os.getenv('PRODUCTION') == 'TRUE':
    # Build the connection string using individual environment variables
    DATABASE_URL = f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    # Use the constructed DATABASE_URL for the database configuration
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    print("Falling back to default SQLite database")
    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.postgresql',
   #         'NAME': os.getenv('DB_NAME'),
   #         'USER': os.getenv('DB_USER'),
   #         'PASSWORD': os.getenv('DB_PASSWORD'),
   #         'HOST': os.getenv('DB_HOST'),
   #         'PORT': os.getenv('DB_PORT', '5432'),  # Default port is 5432
   #     }
   # }

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    },
    'facebook': {
        'APP': {
            'client_id': os.getenv('FACEBOOK_CLIENT_ID'),
            'secret': os.getenv('FACEBOOK_CLIENT_SECRET'),
            'key': ''
        }
    },
    'spotify': {
        'APP': {
            'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
            'secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
            'key': ''
        }
    },
}

# Email settings for development (using console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, use a real SMTP server configuration, for example:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your_email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your_email_password'

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')