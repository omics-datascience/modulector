#!/bin/bash

logger "Starting app..."

while ! python3 tools/test_db_connection.py
do
    echo "Database is still down, retrying in 5 seconds"
    sleep 5
done


python3 manage.py generate_secret_key --settings='ModulectorBackend.settings' && \
python3 manage.py collectstatic --no-input && \
daphne -b 0.0.0.0 -p 8000 ModulectorBackend.asgi:application
