from typing import Optional
from .settings import *
import os

# You can set the SECRET_KEY with an env var or a file generated automatically
secret_key_env = os.getenv('SECRET_KEY')
if secret_key_env is None:
    # Use a separate file for the secret key. Generated with https://pypi.org/project/django-generate-secret-key/
    with open(os.path.join(BASE_DIR, 'secretkey.txt')) as f:
        SECRET_KEY = f.read().strip()
else:
    # Use env var
    SECRET_KEY = secret_key_env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# Disables Django REST Framework browsable API (in production only)
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


# 'web' is the name of the docker-compose service which serves Django
custom_allowed_hosts: Optional[str] = os.getenv('ALLOWED_HOSTS')
if custom_allowed_hosts is None:
    ALLOWED_HOSTS = ['web', 'localhost', '127.0.0.1', '::1']
else:
    # Gets all the hosts declared by the user (separated by commas)
    allowed_host_list = custom_allowed_hosts.split(',')

    # Adds localhost to the list if it's not already there as it's needed for the health check
    if 'localhost' not in allowed_host_list:
        allowed_host_list.append('localhost')

    allowed_host_list_stripped = [x.strip() for x in allowed_host_list]
    ALLOWED_HOSTS = allowed_host_list_stripped

# From Django 4 this needs to be set to prevent issue with NGINX
csrf_trusted_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = csrf_trusted_origins_env.split(',')

# Security settings
ENABLE_SECURITY: bool = os.getenv('ENABLE_SECURITY', 'false') == 'true'
SESSION_COOKIE_SECURE = ENABLE_SECURITY
CSRF_COOKIE_SECURE = ENABLE_SECURITY
SECURE_REFERRER_POLICY = 'same-origin'

# This prevents issues with FileField/ImageField URLs
if ENABLE_SECURITY:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


