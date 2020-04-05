from utils import clean_string, Enum
from markers import Markers

class TodoState(Enum):
    V = "✔"
    X = "❌"

TODO_STATE_FORMAT = {
    None: '{}',
    TodoState.V: '{} ~{{}}~'.format(TodoState.V),
    TodoState.X: '{} {{}}'.format(TodoState.X),
}

class SpecialChars(Enum):
    TODO_LIST_START = '-'
    STRIKETHROUGH = '~'

class Todo:
    def __init__(self, text, state=None):
        self._text = text
        self._state = state

    @classmethod
    def from_string_line(cls, string):
        state = self.get_state_from_string(string)
        text = clean_string(string, *TodoState.to_dict().values(), *SpecialChars.to_dict().values())

        if not text:
            text = '<EMPTY>'

        return cls(text, state)

    @classmethod
    def from_string_message(cls, string):
        for line in string.splitlines():
            todo = cls.from_string_line(line)
            if todo:
                yield todo

    @staticmethod
    def get_state_from_string(string):
        for state in TodoState.to_dict().values():
            if state in string:
                return state
        return None

    @property
    def text(self):
        return self._text

    @property
    def state(self):
        return self._state

    def change_state(self, new_state):
        if self._state == new_state:
            new_state = None # Deselect
        self._state = new_state

    def __str__(self):
        return TODO_STATE_FORMAT[self._state].format(self._text)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self._text, self._state)


class TodosManager:
    def __init__(self):
        self._todos = {}

    @property
    def todos(self):
        return self._todos

    def add_todo_from_message(self, message_id, message_text):
        if message.message_id not in self._todos:
            self._todos[message.message_id] = Todo.from_string_line(message.text)

    def create_todos(self, bot, message):
        try:
            message.delete()
        except:
            logger.exception("Can't delete message")

        for todo in Todo.from_string_message(message.text):
            m = bot.send_message(
                message.chat_id, 
                str(todo), 
                reply_markup=INLINE_KEYBOARD,
            )
            self._todos[m.message_id] = todo

    def update_todo(self, bot, message, selected_state):
        if message.message_id not in self._todos:
            self._todos[message.message_id] = Todo.from_string_line(message.text)
        
        self._todos[message.message_id].change_state(selected_state)
        
        bot.edit_message_text(
            str(self._todos[message.message_id]),
            chat_id=message.chat_id,
            message_id=message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=INLINE_KEYBOARD,
        )
