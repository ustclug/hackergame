from .base import *

DEBUG = False
ALLOWED_HOSTS = ['hgtest.lug.ustc.edu.cn']
MEDIA_ROOT = '/var/opt/hgtest/media'
STATIC_ROOT = '/var/opt/hgtest/static'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hgtest',
        'USER': 'hgtest',
        'CONN_MAX_AGE': 0 if is_gevent_active() else 60,
        'ATOMIC_REQUESTS': True,
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'hgtest',
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
        'request': {
            'format': '%(asctime)s %(ip)s %(userid)s %(levelname)s %(message)s',
        }
    },
    'filters': {
        'add_user_info': {
            '()': 'frontend.utils.UserInfoFilter'
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
        'request': {
            'class': 'logging.StreamHandler',
            'formatter': 'request',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins', 'django.server'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'filters': ['add_user_info'],
            'handlers': ['request'],
            'propagate': False,
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = SMTP_HOSTNAME
EMAIL_PORT = 587
EMAIL_HOST_USER = SMTP_USERNAME
EMAIL_HOST_PASSWORD = SMTP_PASSWORD
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[hgtest] '

GOOGLE_APP_ID = '2574063612-p2ss2hgg9rr7c67n9d0e4g3l6j9gk8v2' \
                '.apps.googleusercontent.com'
MICROSOFT_APP_ID = '6a243fe9-a603-4c6e-b6bd-5af20b7f460e'
SMS_ACCESS_KEY_ID = 'LTAI4FmgeKHNWB7WbTwTP7d9'
