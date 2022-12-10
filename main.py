import config
import todo_bot


def run_gcloud_webhook(request):
    return todo_bot.run_gcloud_webhook(request, config.TELEGRAM_API_TOKEN)
