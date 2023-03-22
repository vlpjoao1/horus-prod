from .base import *
import db

DEBUG = False

# Comentario agregado al allowed host
ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'

DATABASES = db.SQLITE
