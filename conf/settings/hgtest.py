from .base import *

DEBUG = False
ALLOWED_HOSTS = ['hgtest.lug.ustc.edu.cn']
HOST = 'https://hgtest.lug.ustc.edu.cn'
UPLOAD_DIR = '/var/opt/hackergame/file'
STATIC_ROOT = '/var/opt/hackergame/static'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hgtest',
        'USER': 'hgtest',
        'CONN_MAX_AGE': 60,
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'hgtest',
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.s.ustclug.org'
EMAIL_SUBJECT_PREFIX = '[HG-TEST] '

SMS_ACCESS_KEY_ID = 'LTAI4FmgeKHNWB7WbTwTP7d9'
