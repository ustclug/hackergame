import os

from local_settings import *

# Example local_settings:
'''
ALLOWED_HOSTS = ['example.com']
HOST = 'https://example.com'
DEBUG = False
SECRET_KEY = '******'
STATIC_ROOT = '/var/opt/hackergame/static/'
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = '[Hackergame] '
ADMINS = [('Admin', 'admin@example.com')]
DEFAULT_FROM_EMAIL = 'no-reply@example.com'
SERVER_EMAIL = 'root@example.com'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database',
        'USER': 'user',
        'CONN_MAX_AGE': 60,
    },
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    },
}
'''

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if DEBUG:
    ALLOWED_HOSTS += ['localhost', '127.0.0.1', '[::1]']

if DATABASES is None:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
    }

CTF_TEMPLATE_HUB = 'hub.html'
CTF_TEMPLATE_BOARD = 'board.html'

OTP_BACKENDS = [
    'otp.backends.ustc_cas.Ustc',
    'otp.backends.zju_email.Zju',
    'otp.backends.nju_email.Nju',
    'otp.backends.njust_email.Njust',
    'otp.backends.hnu_email.Hnu',
    'otp.backends.uestc_email.Uestc',
    'otp.backends.sjtu_email.Sjtu',
    'otp.backends.email.Email',
]

LOGIN_REDIRECT_URL = 'nickname'
NICKNAME_REDIRECT_URL = 'hub'
LOGOUT_REDIRECT_URL = 'hub'
TERMS_URL = 'terms'
TERMS_REDIRECT_URL = 'hub'

INSTALLED_APPS = [
    'ctf.apps.CtfConfig',
    'logout.apps.LogoutConfig',
    'otp.apps.OtpConfig',
    'terms.apps.TermsConfig',
    'utils.apps.UtilsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hackergame.urls'
STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'ctf.context_processors.ctf',
                'otp.context_processors.otp',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

WSGI_APPLICATION = 'hackergame.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-hans'
