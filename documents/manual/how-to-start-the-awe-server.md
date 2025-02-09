# How to start the AWE server

## 0. Go to the `awe-system-ui` directory

```bash
cd /home/oem/projects/awe-system-ui
```

All the following make commands are simply shortcuts for the following docker compose commands.

You can find details in the `Makefile` (`awe-system-ui/Makefile`).

## 1. Build the images

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
