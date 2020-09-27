from .base import *  # noqa: F401, F403

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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached:11211',
    }
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
        'level': 'INFO',
    },
}

DEBUG = False

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = '/data/media'
STATIC_ROOT = '/data/static'
