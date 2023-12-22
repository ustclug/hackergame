from .hackergame import *
import os

# Official domain and localhost for local test
ALLOWED_HOSTS = ["hack.lug.ustc.edu.cn", '.localhost', '127.0.0.1', '[::1]']
# For local test
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hackergame',
        'USER': 'hackergame',
        'CONN_MAX_AGE': 0,
        'ATOMIC_REQUESTS': True,
        'HOST': 'hackergame-pgbouncer',
        'PORT': 5432,
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': 'hackergame-memcached:11211',
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'hackergame',
    },
}
