import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + "/../curiousWorkbench")
from configSettings import configSettings
configSettingsObj = configSettings()
"""
Django settings for curious project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = configSettingsObj.appFolderPath
dbHost  = configSettingsObj.dbHost
dbUser  = configSettingsObj.dbUser
dbPassword  = configSettingsObj.dbPassword
dbName  = configSettingsObj.dbName
ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_USE_TLS = True
#EMAIL_USE_SSL = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_HOST_USER='AKIAJKZ2J4F5EQNVSUZQ'
EMAIL_HOST_PASSWORD='AmxPcqXNPYVOpdeAsdq3TQGRMiBNOcc9rbLKzUzMZAvE'
DEFAULT_FROM_EMAIL = 'chandan.maruthi@walnutai.com'
DEFAULT_TO_EMAIL = 'chandan.maruthi@walnutai.com'

#print BASE_DIR
#TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)
#print TEMPLATE_DIRS
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^1ydn7xbax7(5r^wwer090))2ywfutf-&@i8-i-s8-5at=0$&j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'test.walnutai.com','test.propl.io']

# Application definition

INSTALLED_APPS = (
    'sslserver',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'curiousWorkbench',
    'registration',
    'rest_framework',
    'mod_wsgi.server',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

ROOT_URLCONF = 'curious.urls'

WSGI_APPLICATION = 'curious.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': dbName,
        'USER': dbUser,
        'PASSWORD': dbPassword,
        'HOST': dbHost,
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

#TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
#print TEMPLATE_DIRS
MEDIA_ROOT = BASE_DIR + '/UserContent/'
MEDIA_URL = '/curiousWorkbench/UserContent/'
LOGIN_URL = '/curiousWorkbench/login/'

#TEMPLATE_LOADERS = ['django.template.loaders.filesystem.Loader',
# 'django.template.loaders.app_directories.Loader']
TEMPLATES = [
{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        configSettingsObj.appFolderPath + '/templates/curiousWorkbench/',
                configSettingsObj.appFolderPath + '/templates/admin/',
        ],
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    'loaders': [
	'django.template.loaders.filesystem.Loader',
 	'django.template.loaders.app_directories.Loader'
	]
    },
},
]
