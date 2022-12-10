import config
import todo_bot

def run(request):
    return todo_bot.run_cloud_function(request, config.TELEGRAM_API_TOKEN)
