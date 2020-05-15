import re
from simple_enum import SimpleEnum
from string_utils import clean_string

class TodoState(SimpleEnum):
    V = "✔"
    X = "❌"

_TODO_STATE_FORMAT = {
    None: '{}',
    TodoState.V: '{} ~{{}}~'.format(TodoState.V),
    TodoState.X: '{} {{}}'.format(TodoState.X),
}

TODO_LIST_START_MARKER = '-'
TODO_LIST_START_REGEX = re.compile('^{}'.format(TODO_LIST_START_MARKER))

_CHARATERS_TO_REMOVE = [
    TodoState.V,
    TodoState.X,
    TODO_LIST_START_MARKER,
    '~',
]

class Todo:
    def __init__(self, text, state=None):
        self._text = re.escape(text)
        self._state = state

    @classmethod
    def from_todo_message_text(cls, string):
        state = cls.get_state_from_string(string)
        text = clean_string(string, *_CHARATERS_TO_REMOVE)

        if text:
            return cls(text, state)
        return None

    @classmethod
    def from_todo_list_message_text(cls, string):
        for line in string.splitlines():
            todo = cls.from_todo_message_text(line)
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
        return _TODO_STATE_FORMAT[self._state].format(self._text)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self._text, self._state)
