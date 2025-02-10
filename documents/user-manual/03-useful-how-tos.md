# Some useful how-tos

## Turn on/off the email notification when batch processing is finished

Add a line to the `.envs/.production/.secrets` file:

```config
# Turn on (default)
NOTIFY_BATCH_COMPLETION=True

# Turn off
NOTIFY_BATCH_COMPLETION=False
```

Then restart the server.

```bash
make restart-production
```
