from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
MEDIA_ROOT = 'var/media'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'var/db.sqlite3',
        'ATOMIC_REQUESTS': True,
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'request': {
            'format': '%(asctime)s %(ip)s %(userid)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'add_user_info': {
            '()': 'frontend.utils.UserInfoFilter'
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['databaselog'],
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['databaselog'],
        },
        'django.request': {
            'filters': ['add_user_info'],
            'handlers': ['request'],
            'propagate': False,
        },
    },
    'handlers': {
        'databaselog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'var/database.log',
            'mode': 'w',
        },
        'request': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'request',
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

GOOGLE_APP_ID = '2574063612-e44k22j4071rjntvm9rpkgipv1u85svm' \
                '.apps.googleusercontent.com'
MICROSOFT_APP_ID = '6a243fe9-a603-4c6e-b6bd-5af20b7f460e'
SMS_ACCESS_KEY_ID = 'LTAI4FmgeKHNWB7WbTwTP7d9'
