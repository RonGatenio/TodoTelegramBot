import os

TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
WEBHOOK_PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")