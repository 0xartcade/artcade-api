#####################################
### RUFF
#####################################
fmt:
	poetry run ruff format .

# lint code
lint:
	poetry run ruff check --fix .

#####################################
### DJANGO
#####################################
migrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate

superuser:
	poetry run python manage.py createsuperuser

run-server:
	poetry run gunicorn api.wsgi:application -k gevent --bind :8000 --reload

run-celery:
	poetry run celery -A api.celery purge --force
	poetry run celery -A api.celery worker -Q p0,p1,p2,celery -P gevent -c 10

run-infra:
	docker compose -f docker-compose.local.yaml up -d

stop-infra:
	docker compose -f docker-compose.local.yaml down

#####################################
### TESTING
#####################################
test:
	poetry run pytest

unit-test:
	poetry run pytest tests/unit

func-test:
	poetry run pytest tests/functional