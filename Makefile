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

run-infra:
	docker compose -f docker-compose.local.yaml up -d

stop-infra:
	docker compose -f docker-compose.local.yaml down

run-server:
	poetry run gunicorn api.wsgi -k gevent --bind :8000 --reload

run-huey:
	poetry run manage.py run_huey

#####################################
### TESTING
#####################################
test:
	poetry run pytest

unit-test:
	poetry run pytest tests/unit

func-test:
	poetry run pytest tests/functional