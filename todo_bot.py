import telegram
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram.ext.filters import Filters

from logging_utils import init_logger
from telegram_utils import make_inline_keyboard
from todo import Todo, TodoState, TODO_LIST_START_REGEX


LOGGER = init_logger(__name__)

INLINE_KEYBOARD = make_inline_keyboard(TodoState.V, TodoState.X)

START_MESSAGE = \
"""
I'm the *TodoBot*

Add TODOs and have fun\!

For help: /help
"""

HELP_MESSAGE = \
"""
*TodoBot Help*
To add a TODO, start a message with '\-'\.
The message can have multiple lines\. Each line will turn into a separated TODO\.

Todos are given an inline keyboard with 2 options: {} {}\.
Click on them to mark the todo\.

*TodoBot Commands*
/start \- Shows the start message\.
/help \- Shows this message\.

I'm also on [GitHub](https://github.com/RonGatenio/TodoTelegramBot)
""".format(TodoState.V, TodoState.X)


def _todo_list_message_handler(update, context):
    message = update.effective_message

    try:
        message.delete()
    except:
        LOGGER.exception("Can't delete message: {}".format(message.to_dict()))

    for todo in Todo.from_todo_list_message_text(message.text):
        try:
            context.bot.send_message(
                message.chat_id, 
                str(todo), 
                reply_markup=INLINE_KEYBOARD,
            )
        except:
            LOGGER.exception("Can't send {}".format(repr(todo)))


def _keyboard_click_handler(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    message = update.effective_message
    selected_state = query.data

    todo = Todo.from_todo_message_text(message.text)
    todo.change_state(selected_state)

    query.edit_message_text(
        str(todo),
        parse_mode=ParseMode.HTML,
        reply_markup=INLINE_KEYBOARD,
    )


def _start_command_handler(update, context):
    message = update.effective_message

    context.bot.send_message(
        message.chat_id, 
        START_MESSAGE,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def _help_command_handler(update, context):
    message = update.effective_message

    context.bot.send_message(
        message.chat_id, 
        HELP_MESSAGE,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def _error_handler(update, context):
    """Log Errors caused by Updates."""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


def _init_updater(api_token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(api_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', _start_command_handler))
    updater.dispatcher.add_handler(CommandHandler('help', _help_command_handler))
    
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(TODO_LIST_START_REGEX), _todo_list_message_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(_keyboard_click_handler))

    updater.dispatcher.add_error_handler(_error_handler)

    return updater


def run_cloud_function(request, api_token):
    if request.method == "POST":
        updater = _init_updater(api_token)
        update = telegram.Update.de_json(request.get_json(force=True), updater.bot)
        updater.dispatcher.process_update(update)
    return 'OK'


def run_polling(api_token):
    updater = _init_updater(api_token)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


def run_webhooks(api_token, base_url, port):
    updater = _init_updater(api_token)
    
    updater.start_webhook(
        listen='0.0.0.0',
        port=port,
        url_path=api_token,
    )
    updater.bot.set_webhook('{}/{}'.format(base_url, api_token))
