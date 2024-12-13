worker: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn api.wsgi:application -k gevent --workers 3 --timeout 60 --worker-tmp-dir /dev/shm
