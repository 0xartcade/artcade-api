release: python manage.py migrate --noinput
release: python manage.py collectstatic --noinput
web: gunicorn api.wsgi:application -k gevent --bind :8000 --workers 3 --timeout 60 --worker-tmp-dir /dev/sh
