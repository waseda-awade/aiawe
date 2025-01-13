build-local:
	docker compose -f docker-compose.local.yml build

run-local:
	docker compose -f docker-compose.local.yml up -d

run-local-debug:
	docker compose -f docker-compose.local.yml -f docker-compose.debug.yml up -d

stop-local:
	docker compose -f docker-compose.local.yml down

restart-local:
	docker compose -f docker-compose.local.yml down && docker compose -f docker-compose.local.yml up -d

csu:
	docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser

mm:
	docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

mi:
	docker compose -f docker-compose.local.yml run --rm django python manage.py migrate

pc:
	pipenv run pre-commit run --all-files
