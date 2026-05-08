#!/bin/sh
set -e

echo "Waiting 10 seconds for database to be ready..."
sleep 10

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Starting server..."
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application