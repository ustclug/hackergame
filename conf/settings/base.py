from ..local_settings import *

ROOT_URLCONF = 'frontend.urls'
WSGI_APPLICATION = 'frontend.wsgi.application'
INSTALLED_APPS = [
    'frontend.apps.FrontendConfig',
    'server.announcement.apps.AnnouncementConfig',
    'server.challenge.apps.ChallengeConfig',
    'server.submission.apps.SubmissionConfig',
    'server.terms.apps.TermsConfig',
    'server.trigger.apps.TriggerConfig',
    'server.user.apps.UserConfig',
    'apps.otp.apps.OtpConfig',
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

# Database
ATOMIC_REQUESTS = True

# Static
STATIC_URL = '/static/'

# Template
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'frontend.context_processors.frontend',
                'apps.otp.context_processors.otp',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Email
EMAIL_SUBJECT_PREFIX = '[Hackergame] '
ADMINS = [('Hypercube', 'hypercube@0x01.me')]
DEFAULT_FROM_EMAIL = 'hack@lug.ustc.edu.cn'
SERVER_EMAIL = 'hack@lug.ustc.edu.cn'

# I18N and L10N
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-Hans'

# otp
LOGIN_REDIRECT_URL = 'hub'
OTP_BACKENDS = [
    'apps.otp.backends.ustc_cas.Ustc',
    'apps.otp.backends.nankai_email.Nankai',
    'apps.otp.backends.sms.Sms',
]
