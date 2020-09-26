from .base import *

INSTALLED_APPS = ['debug_toolbar'] + INSTALLED_APPS
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '72$l4ihy2rc&ogh55a#5%xhubl^3n)eli9a$!@e5_eankk2oo='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hackergame',
        'USER': 'hackergame',
        'CONN_MAX_AGE': 60,
        'ATOMIC_REQUESTS': True,
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django.server': {
            'handlers': ['databaselog'],
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['databaselog'],
        },
    },
    'handlers': {
        'databaselog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'database.log'),
            'mode': 'w',
        },
    },
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INTERNAL_IPS = ['127.0.0.1']
