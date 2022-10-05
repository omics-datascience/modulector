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
custom_allowed_hosts: Optional[str] = os.getenv('CUSTOM_ALLOWED_HOSTS')
if custom_allowed_hosts is None:
    ALLOWED_HOSTS = ['web','.localhost', '127.0.0.1', '[::1]']
else:
    # Gets all the hosts declared by the user (separated by commas)
    allowed_host_list = custom_allowed_hosts.split(',')
    allowed_host_list_stripped = [x.strip() for x in allowed_host_list]
    ALLOWED_HOSTS = allowed_host_list_stripped

# Security settings
# SESSION_COOKIE_SECURE = True  # TODO: set when configured a SSL Cert.
# CSRF_COOKIE_SECURE = True  # TODO: set when configured a SSL Cert.
SECURE_REFERRER_POLICY = 'same-origin'

