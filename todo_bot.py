import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, PicklePersistence
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from telegram.ext.filters import Filters
from telegram import ParseMode

from context_manager import add_new_message, get_messages_by_marker, remove_messages_by_marker, get_messages, set_message_marker


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Markers:
    V = "✔"
    X = "❌"

def make_inline_keyboard(*buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(button, callback_data=button) for button in buttons]])

INLINE_KEYBOARD = make_inline_keyboard(Markers.V, Markers.X)


def _message_handler(update, context):
    message = update.effective_message

    from pprint import pprint
    try:
        pprint(update.to_dict())
    except:
        pprint(update)

    message.delete()

    for line in message.text.splitlines():
        item_text = line.replace('-', '').strip()

        m = context.bot.send_message(message.chat_id, item_text, reply_markup=INLINE_KEYBOARD)
        add_new_message(context, m.message_id, item_text)


def _clean_command_handler(update, context):
    message = update.message
    message.delete()

    for message_id in get_messages_by_marker(context, Markers.V):
        context.bot.delete_message(message.chat_id, message_id)

    remove_messages_by_marker(context, Markers.V)


def _keyboard_click_handler(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    message = query.message

    if message.message_id not in get_messages(context):
        return
    message_data = get_messages(context)[message.message_id]
    
    if message_data.marker == query.data:
        return

    if query.data == Markers.V:
        txt = '{} ~{}~'.format(Markers.V, message_data.text)
    elif query.data == Markers.X:
        txt = '{} {}'.format(Markers.X, message_data.text)
    query.edit_message_text(txt, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=INLINE_KEYBOARD)
    
    set_message_marker(context, message.message_id, query.data)


def _error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def run(api_token, presistence_storage_filename='todobot.dat'):
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename=presistence_storage_filename)
    updater = Updater(api_token, persistence=pp, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('clean', _clean_command_handler))
    updater.dispatcher.add_handler(CommandHandler('list', _clean_command_handler))
    updater.dispatcher.add_handler(CommandHandler('list_x', _clean_command_handler))
    updater.dispatcher.add_handler(CommandHandler('list_v', _clean_command_handler))
    
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^-'), _message_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(_keyboard_click_handler))

    updater.dispatcher.add_error_handler(_error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
