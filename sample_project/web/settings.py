# -*- coding: utf-8 -*-
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent

SECRET_KEY = 'secret_key'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
	'django_sample_generator',
	'web',
]

MIDDLEWARE = [
]

ROOT_URLCONF = 'web.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
	},
]

WSGI_APPLICATION = 'web.wsgi.application'


DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': BASE_DIR / 'db.sqlite3',
	}
}

SAMPLE_DATA_GENERATORS = (
	'web.generators',
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_TZ = False

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
