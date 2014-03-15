# -*- coding: utf-8 -*-

##
## WARNING PLEASE READ
##
## This is the generic configuration file of the blogmeter django project.
## No changes should be made to this file, instead use the local_settings.py
## file to make any change you might need.
##

import datetime
import os.path
project_dir = os.path.abspath ( os.path.join( os.path.dirname( __file__ ), '../..' ))
django_dir = os.path.abspath ( os.path.join( os.path.dirname( __file__ ), '..' ))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

SQLITEFILE = os.path.join(django_dir, 'bmdjango.db')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': SQLITEFILE,                     # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Lisbon'

##
## Language
##

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

##
## Media
##

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join( django_dir, 'static' ),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

##
## Other suff
##

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'dg77vxuxn3jr5w7*(4j00*w6p@-9#yymq3*wrg%qt7_*o&5x9v'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'utils.middleware.threadlocals.ThreadLocals',
)

ROOT_URLCONF = 'bmdjango.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bmdjango.wsgi.application'


##
## Templates
##

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join( django_dir, 'templates' ),
)


##
## Apps
##

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Admin app:
    'django.contrib.messages',
    'django.contrib.admin',

    # Blogmeter apps:
    'meter',
    'authapp',
    'registrationapp'
)


##
## Logging
##

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

import sys

LOGDIR  = os.path.join(project_dir, '..', 'log')
LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                },
            'simple': {
                'format': '%(levelname)s %(message)s'
                }
            },
        'handlers': {
            'console': {
                'level':'DEBUG',
                'class':'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter':'simple'
                },
            'default': {
                'level':'INFO',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOGDIR, 'blogometro.log'),
                'maxBytes': 1024*1024*50, # 50MB
                'backupCount': 5,
                'formatter':'verbose',
                },

            },
        'loggers': {
            'django': {
                'handlers':['default'],
                'filters': [],
                'propagate': True,
                'level':'DEBUG',
                },
            'webscraper': {
                'handlers':['console','default'],
                'filters': [],
                'propagate': True,
                'level':'INFO',
                },
            },
        }


##
## Authentication and sessions
##

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 24 * 3600 * 14   # 14 days
SESSION_COOKIE_SECURE = False    # set to True if using https
SESSION_COOKIE_NAME = 'blogmeter_sessionid'

LOGIN_URL   = '/auth/login/'
LOGOUT_URL  = '/auth/logout/'

LOGIN_REDIRECT_URL = '/'

REMEMBER_LOGIN = True

FAILURE_LIMIT= 3 # number of failed attempts

## CAPTCHA CONFIGURATION
## This keys work only for local testing at 127.0.0.1!
RECAPTCHA_PUB_KEY = '6Lcc-AAAAAAAAN4NOVSI_E9oPvilVrvDDuoVXsgJ'
RECAPTCHA_PRIV_KEY = '6Lcc-AAAAAAAAOztgVgg9SHtgYknCkvo42B7vBCf'
RECAPTCHA_THEME = 'white'

# Registration
PASSWORD_MIN_SIZE = 3
PASSWORD_MAX_SIZE = 30

##
## Blogmeter specific
##

# At what time should we start showing the current day stats:
CHANGE_DAY = datetime.time(2,0,0)

##
## LOCAL
##

try:
    from local_settings import *
except ImportError:
    pass

