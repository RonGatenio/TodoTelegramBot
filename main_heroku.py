import config
import todo_bot

if __name__ == "__main__":
    todo_bot.run_webhooks(
        api_token=config.TELEGRAM_API_TOKEN,
        base_url='https://{}.herokuapp.com'.format(config.HEROKU_APP_NAME),
        port=config.HEROKU_WEBHOOK_PORT
    )
