from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
HOST = 'https://non-exist.lug.ustc.edu.cn'
UPLOAD_DIR = 'var/file'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'var/db.sqlite3',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SMS_ACCESS_KEY_ID = 'LTAI4FmgeKHNWB7WbTwTP7d9'
