#!/bin/bash
logger "Starting app..."

python3 manage.py generate_secret_key --settings='ModulectorBackend.settings' && python3 manage.py collectstatic --no-input && python3 manage.py makemigrations && python3 manage.py migrate && daphne -b 0.0.0.0 -p 8000 ModulectorBackend.asgi:application