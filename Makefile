csu:
	docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser

mm:
	docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

mi:
	docker compose -f docker-compose.local.yml run --rm django python manage.py migrate

pc:
	pipenv run pre-commit run --all-files
