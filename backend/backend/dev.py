from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '72$l4ihy2rc&ogh55a#5%xhubl^3n)eli9a$!@e5_eankk2oo='
PRIVATE_KEY = '''
-----BEGIN EC PRIVATE KEY-----
MHQCAQEEIKLQaa4PTPdXPSnkYFRLUDFx9jxCMESfuSjfSwOSf24coAcGBSuBBAAK
oUQDQgAESRXjz5yiRDRFWNFPTAb3o75Do6KWMR2E21Jr3HxeW/teDO3gAbcqbn8J
WsoHj98qPDXf91kBRHBp8rEgVwEvrQ==
-----END EC PRIVATE KEY-----
'''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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
