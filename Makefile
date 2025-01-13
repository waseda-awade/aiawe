# Replace the % with the desired environment, e.g. `make run-local` for local environment
# or `make run-production` for production environment

build-%:
	docker compose -f docker-compose.$*.yml build

run-%:
	docker compose -f docker-compose.$*.yml up -d

run-local-debug:
	docker compose -f docker-compose.local.yml -f docker-compose.debug.yml up -d

stop-%:
	docker compose -f docker-compose.$*.yml down

restart-%:
	docker compose -f docker-compose.$*.yml restart

# Create a superuser
csu-%:
	docker compose -f docker-compose.$*.yml run --rm django python manage.py createsuperuser

mm:
	docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

mi:
	docker compose -f docker-compose.local.yml run --rm django python manage.py migrate

pc:
	pipenv run pre-commit run --all-files

rm-static-vol:
	docker volume rm awe_system_ui_production_django_static
