import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, PicklePersistence
from telegram.ext.filters import Filters
from todo_data import TodosManager, TODO_LIST_START_REGEX, Markers


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_todos_manager(context) -> TodosManager:
    if 'todos_manager' not in context.chat_data:
        context.chat_data['todos_manager'] = TodosManager()
    return context.chat_data['todos_manager']


def _message_handler(update, context):
    todos_manager = _get_todos_manager(context)

    todos_manager.create_todos_from_message(context.bot, update.effective_message)


def _clean_command_handler(update, context):
    todos_manager = _get_todos_manager(context)

    message = update.effective_message
    message.delete()

    for message_id in todos_manager.get_todos_by_marker(Markers.V):
        del todos_manager.todos[message_id]
        try:
            context.bot.delete_message(message.chat_id, message_id)
        except:
            logger.exception("Can't delete message")


def _keyboard_click_handler(update, context):
    todos_manager = _get_todos_manager(context)

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    todos_manager.update_todo(context.bot, update.effective_message, query.data)


def _list_todos(update, context, marker):
    update.effective_message.delete()
    todos_manager = _get_todos_manager(context)
    message = '\n'.join([todo.text for todo in todos_manager.get_todos_by_marker(marker).values()])
    if message:
        context.bot.send_message(update.effective_message.chat_id, message)


def _list_command_handler(update, context):
    _list_todos(update, context, None)


def _list_v_command_handler(update, context):
    _list_todos(update, context, Markers.V)


def _list_x_command_handler(update, context):
    _list_todos(update, context, Markers.X)


def _error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def run(api_token, presistence_storage_filename='todobot.dat'):
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename=presistence_storage_filename)
    updater = Updater(api_token, persistence=pp, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('clean', _clean_command_handler))
    updater.dispatcher.add_handler(CommandHandler('list', _list_command_handler))
    updater.dispatcher.add_handler(CommandHandler('list_v', _list_v_command_handler))
    updater.dispatcher.add_handler(CommandHandler('list_x', _list_x_command_handler))
    
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(TODO_LIST_START_REGEX), _message_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(_keyboard_click_handler))

    updater.dispatcher.add_error_handler(_error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
