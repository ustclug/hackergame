from .hackergame import *

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': 'memcached:11211',
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'hackergame',
    },
}
