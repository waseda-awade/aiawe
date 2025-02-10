# Some useful how-tos

## Turn on/off the email notification when batch processing is finished

Add a line to the `.envs/.production/.secrets` file:

```config
# Turn on (default)
NOTIFY_BATCH_COMPLETION=True

# Turn off
NOTIFY_BATCH_COMPLETION=False
```

Then full restart the server.

```bash
make frestart-production
```

## How to change the port number of the Django server

Change the port number `8001` to your own port number in the `docker-compose.production.yml` file:

```yml
services:
  ...
  traefik:
    ...
    ports:
      - '8001:80'
```

Then full restart the server.

```bash
make frestart-production
```
