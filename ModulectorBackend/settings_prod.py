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

# 'web' is the name of the docker-compose service which serves Django
ALLOWED_HOSTS = ['web']

# Security settings
# SESSION_COOKIE_SECURE = True  # TODO: set when configured a SSL Cert.
# CSRF_COOKIE_SECURE = True  # TODO: set when configured a SSL Cert.
SECURE_REFERRER_POLICY = 'same-origin'

