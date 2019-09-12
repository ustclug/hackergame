from ..local_settings import *

ROOT_URLCONF = 'server.urls'
WSGI_APPLICATION = 'server.wsgi.application'
INSTALLED_APPS = [
    'server.ctf.apps.CtfConfig',
    'server.local.apps.LocalConfig',
    'server.logout.apps.LogoutConfig',
    'server.otp.apps.OtpConfig',
    'server.profile.apps.ProfileConfig',
    'server.terms.apps.TermsConfig',
    'server.token.apps.TokenConfig',
    'server.upload.apps.UploadConfig',
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

# Static
STATIC_URL = '/static/'
STATICFILES_DIRS = ['static']

# Template
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'server.ctf.context_processors.ctf',
                'server.otp.context_processors.otp',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Auth
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Email
EMAIL_SUBJECT_PREFIX = '[Hackergame] '
ADMINS = [('Admin', 'hackergame@ustclug.org'), ('Hypercube', 'hypercube@0x01.me')]
DEFAULT_FROM_EMAIL = 'hackergame@ustclug.org'
SERVER_EMAIL = 'hackergame@ustclug.org'

# I18N and L10N
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-Hans'

# ctf
CTF_TEMPLATE_HUB = 'hub.html'
CTF_TEMPLATE_BOARD = 'board.html'

# logout
LOGOUT_REDIRECT_URL = 'hub'

# otp
LOGIN_REDIRECT_URL = 'profile'
OTP_BACKENDS = [
    'server.otp.backends.ustc_cas.Ustc',
    'server.otp.backends.zju_email.Zju',
    'server.otp.backends.nju_email.Nju',
    'server.otp.backends.njust_email.Njust',
    'server.otp.backends.hnu_email.Hnu',
    'server.otp.backends.uestc_email.Uestc',
    'server.otp.backends.sjtu_email.Sjtu',
    'server.otp.backends.edu_email.EduEmail',
    'server.otp.backends.dummy_email.DummyEmail',
    'server.otp.backends.sms.Sms',
]

# profile
PROFILE_REDIRECT_URL = 'hub'

# terms
TERMS_URL = 'terms'
TERMS_REDIRECT_URL = 'hub'

# token
TOKEN_REDIRECT_URL = 'hub'

# upload
UPLOAD_TEMPLATE_UPLOAD = 'upload.html'
