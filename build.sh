#!/usr/bin/env bash
# Render build step for the Django API.
# Exit on any error so a failed migration fails the deploy.
set -o errexit

pip install -r requirements.txt

# Compress + hash static files for WhiteNoise to serve.
python manage.py collectstatic --no-input

# Apply schema, then load demo content (idempotent — safe every deploy).
if [ -n "$DATABASE_URL" ]; then
    python manage.py migrate --no-input
    python manage.py seed_articles
fi
