from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']
HOST = 'https://non-exist.lug.ustc.edu.cn'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'var/db.sqlite3',
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
            'filename': 'var/database.log',
            'mode': 'w',
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SMS_ACCESS_KEY_ID = 'LTAI4FmgeKHNWB7WbTwTP7d9'

OTP_BACKENDS.append('apps.otp.backends.console.Console')
