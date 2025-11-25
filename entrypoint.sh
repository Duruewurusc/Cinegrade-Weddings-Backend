#!/bin/sh
# wait-for-db (optional) can be added
set -e

# apply DB migrations
python manage.py migrate --noinput

# collect static files
python manage.py collectstatic --noinput

# create superuser step is optional; do it manually when needed
exec "$@"
