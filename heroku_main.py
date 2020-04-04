import config
import todo_bot

if __name__ == "__main__":
    todo_bot.run(config.TELEGRAM_API_TOKEN, mode='prod')
