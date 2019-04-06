"""
Django settings for ops project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import cmdb


CELERY_BROKER_URL= 'amqp://admin:ablejava@172.22.0.69:5672/vhost'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jmigexn!efomnp!h53ff%%q*_zb+m-h9m0w7w^**pzfa)7oobn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['47.110.245.93',]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'bootstrap4',
    'cmdb',
    'monitor',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_crontab',
    'manager_redis',


]
SITE_IDSITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ops.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ops.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#          'ENGINE': 'django.db.backends.sqlite3',
#          'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#      }
#  }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wangyue',
        'USER': 'wangyue',
        'PASSWORD':'wangyue_123',
        'HOST':'120.27.148.6',
        'PORT':'3306',
        #'OPTIONS':{'init_command':"SET sql_mode='STRICT_TRANS_TABLES'",'charset':'utf8mb4','sql_mode': 'traditional',}
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'




#/root/anaconda3/bin/python manage.py crontab list
#/root/anaconda3/bin/python manage.py crontab -h
#/root/anaconda3/bin/python manage.py crontab show
#/root/anaconda3/bin/python manage.py crontab add
CRONJOBS = [
    #('*/5 * * * *','cmdb.cron.test'),
    ('*/5 * * * *','cmdb.cron.monitor_url'),
    ('*/1 * * * *','cmdb.cron.dubbo_mon'),
    ('01 * * * *','cmdb.cron.get_request_time'),
    ('59 23 * * *','cmdb.cron.ger_slow_uri')
]
