# How to start the AiAWE server

## 0. Go to the `awe-system-ui` directory

```bash
cd /home/oem/projects/awe-system-ui
```

### Make sure the environment files are set up

```bash
# Copy the example files
cp ./envs/.production/.secrets.example ./envs/.production/.secrets
cp ./envs/.production/.env.production.example ./envs/.production/.env.production

# Edit the files
nano ./envs/.production/.secrets
nano ./envs/.production/.env.production
```

Some important notes for the `.env.secrets` file:

- `DJANGO_DOMAIN_NAME`: The domain name of the server. (e.g., `app.awade.gec.waseda.ac.jp`)
- `DJANGO_SECRET_KEY`: The secret key for the Django server, replace it with a random string.
- `DJANGO_ALLOWED_HOSTS`: The allowed hosts for the Django server, change it to your own domain name.
- `DJANGO_SUPERUSER_EMAIL`: The email for the default superuser to be created the first time.
- `DJANGO_SUPERUSER_PASSWORD`: The password for the default superuser to be created the first time.
- `DJANGO_DEFAULT_FROM_EMAIL`: The default address to send emails from.
- `MAILJET_API_KEY`: The API key for the Mailjet service.
- `MAILJET_SECRET_KEY`: The secret key for the Mailjet service.

Some important notes for the `.env.production` file:

- `VITE_API_BASE_URL`: Set it to the API endpoint of the server, this will be used by the frontend to send requests to the server. (e.g., `https://app.awade.gec.waseda.ac.jp/api`)

## 1. Build the images

> All the following make commands are simply shortcuts for the following docker compose commands.
> You can find details in the `Makefile` (`awe-system-ui/Makefile`).

```bash
make build-production
# or
docker compose -f docker-compose.production.yml build
```

## 2. Start the server

```bash
# this is just a shortcut for the following command
make start-production
# or
docker compose -f docker-compose.production.yml up -d
```

## 3. Stop the server

```bash
make stop-production
# or
docker compose -f docker-compose.production.yml down
```

## 4. Full restart the server

```bash
make frestart-production
# or
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml up -d
```
