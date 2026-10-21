#!/bin/sh
set -e

# Run database migrations and seeding when starting the web service
case "$1" in
    web)
        if [ -n "$DATABASE_URL" ]; then
            echo "Applying database migrations..."
            python manage.py migrate --no-input

            echo "Seeding demo articles..."
            python manage.py seed_articles || echo "Seeding completed or already applied."
        else
            echo "DATABASE_URL not set; skipping automated migrations and seeding."
        fi

        echo "Starting Gunicorn server on 0.0.0.0:${PORT:-8000}..."
        exec gunicorn authors.wsgi:application \
            --bind "0.0.0.0:${PORT:-8000}" \
            --workers 3 \
            --threads 2 \
            --timeout 120
        ;;
    gunicorn*)
        if [ -n "$DATABASE_URL" ]; then
            echo "Applying database migrations..."
            python manage.py migrate --no-input

            echo "Seeding demo articles..."
            python manage.py seed_articles || echo "Seeding completed or already applied."
        else
            echo "DATABASE_URL not set; skipping automated migrations and seeding."
        fi

        export GUNICORN_CMD_ARGS="--bind=0.0.0.0:${PORT:-8000} ${GUNICORN_CMD_ARGS}"
        exec "$@"
        ;;
    *)
        exec "$@"
        ;;
esac
