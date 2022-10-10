from .base import *

DEBUG = False
ALLOWED_HOSTS = ['hack.lug.ustc.edu.cn']
MEDIA_ROOT = '/var/opt/hackergame/media'
STATIC_ROOT = '/var/opt/hackergame/static'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hackergame',
        'USER': 'hackergame',
        'CONN_MAX_AGE': 60,
        'ATOMIC_REQUESTS': True,
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'hackergame',
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 365 * 86400
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'frontend.utils.ThrottledAdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = SES_USERNAME
EMAIL_HOST_PASSWORD = SES_PASSWORD
EMAIL_USE_TLS = True

GOOGLE_APP_ID = '2574063612-kstsrirbttbimgk2da2ju1mmbh8t0ogk' \
                '.apps.googleusercontent.com'
MICROSOFT_APP_ID = '6474be41-5098-4bbe-80dc-95d7ae9660a5'
SMS_ACCESS_KEY_ID = 'LTAI4FmgeKHNWB7WbTwTP7d9'
