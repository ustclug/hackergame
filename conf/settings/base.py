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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
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

# Auth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Media
MEDIA_URL = '/media/'

# Site
SITE_ID = 1

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
DEFAULT_FROM_EMAIL_NAME = 'Hackergame'
DEFAULT_FROM_EMAIL_EMAIL = 'hack@lug.ustc.edu.cn'
DEFAULT_FROM_EMAIL = f'{DEFAULT_FROM_EMAIL_NAME} <{DEFAULT_FROM_EMAIL_EMAIL}>'
SERVER_EMAIL = 'hack@lug.ustc.edu.cn'

# I18N and L10N
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-Hans'

# allauth
LOGIN_REDIRECT_URL = 'hub'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_ADAPTER = 'frontend.adapters.SocialAccountAdapter'
ACCOUNT_EMAIL_VERIFICATION = 'none'
