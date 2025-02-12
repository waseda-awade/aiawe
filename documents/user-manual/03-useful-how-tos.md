# Some useful how-tos

## How to change the dashboard image

Copy the new image to the `vue_frontend/src/assets/imgs/aiawe-dashboard.png` file.

If you have a different name/extension for the image, you can change the `src` attribute in the `vue_frontend\src\views\HomeView.vue` file.

```vue
src="@/assets/imgs/aiawe-dashboard.png"
```

If you want to change the image size, you can change the `max-w-6xl` to `max-w-4xl` or `max-w-3xl` in the `vue_frontend\src\views\HomeView.vue` file.

```vue
<div class="mt-8 max-w-6xl mx-auto">
```

After making the changes, you need to restart the server.

```bash
make frestart-production
```

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
