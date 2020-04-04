import logging
import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ParseMode

logger = logging.getLogger(__name__)

class Markers:
    V = "✔"
    X = "❌"
    MINUS = '-'

def make_inline_keyboard(*buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(button, callback_data=button) for button in buttons]])

INLINE_KEYBOARD = make_inline_keyboard(Markers.V, Markers.X)


TODO_LIST_START_MARKER = Markers.MINUS
TODO_LIST_START_REGEX = re.compile('^{}'.format(TODO_LIST_START_MARKER))


class TodoData:
    def __init__(self, text, marker=None):
        self._text = text
        self._marker = marker

    @classmethod
    def _from_list_message(cls, todos_list_message):
        for line in todos_list_message.splitlines():
            text = line \
                .replace(TODO_LIST_START_MARKER, '') \
                .replace(Markers.V, '') \
                .replace(Markers.X, '') \
                .replace('~', '') \
                .strip()
            if text:
                yield cls(text)

    @classmethod
    def from_message(cls, message):
        return cls._from_list_message(message.text)

    @classmethod
    def from_single_lined_message(cls, message):
        messages = list(cls._from_list_message(message.text))
        assert len(messages) == 1
        return messages[0]

    @property
    def text(self):
        return self._text

    @property
    def marker(self):
        return self._marker

    @marker.setter
    def marker(self, x):
        self._marker = x

    def __str__(self):
        if not self._marker:
            return self._text
        elif self._marker == Markers.V:
            return '{} ~{}~'.format(Markers.V, self._text)
        elif self._marker == Markers.X:
            return '{} {}'.format(Markers.X, self._text)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self._text, self._marker)


class TodosManager:
    def __init__(self):
        self._todos = {}

    @property
    def todos(self):
        return self._todos

    def create_todos_from_message(self, bot, message):
        try:
            message.delete()
        except:
            logger.exception("Can't delete message")

        for todo in TodoData.from_message(message):
            m = bot.send_message(
                message.chat_id, 
                str(todo), 
                reply_markup=INLINE_KEYBOARD,
            )
            self._todos[m.message_id] = todo

    def update_todo(self, bot, message, new_marker):
        if message.message_id not in self._todos:
            self._todos[message.message_id] = TodoData.from_single_lined_message(message)
        
        if self._todos[message.message_id].marker == new_marker:
            return

        self._todos[message.message_id].marker = new_marker
        bot.edit_message_text(
            str(self._todos[message.message_id]),
            chat_id=message.chat_id,
            message_id=message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=INLINE_KEYBOARD,
        )

    def get_todos_by_marker(self, marker):
        return {k: v for k, v in self._todos.items() if v.marker == marker}

    def printme(self):
        from pprint import pprint
        pprint(self.todos)
