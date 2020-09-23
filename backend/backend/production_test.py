from .base import *

with open('/data/secret.key') as f:
    SECRET_KEY = f.read().strip()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hackergame',
        'USER': 'hackergame',
        'PASSWORD': 'hackergame',
        'HOST': 'database',
        'CONN_MAX_AGE': 60,
        'ATOMIC_REQUESTS': True,
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

DEBUG = True  # This should be false in production server

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = '/data/media'
STATIC_ROOT = '/data/static'
