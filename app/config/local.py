from .base import *
import config.db as db

DEBUG = True

# Comentario agregado al allowed host
ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'

DATABASES = db.SQLITE
