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

runserver:
	poetry run gunicorn api.wsgi:application -k gevent --bind :8000 --reload

runcelery:
	poetry run celery -A api.celery purge --force
	poetry run celery -A api.celery worker -P gevent -c 10

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