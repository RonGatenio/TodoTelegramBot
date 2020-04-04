from collections import namedtuple


DEFAULT_MARKER = None

MessageData = namedtuple('MessageData', ['text', 'marker'])


def add_new_message(context, id, text, default_marker=DEFAULT_MARKER):
    if 'messages' not in context.chat_data:
        context.chat_data['messages'] = {}

    context.chat_data['messages'][id] = MessageData(text, default_marker)


def set_message_marker(context, id, marker):
    messages = get_messages(context)
    if id in messages:
        messages[id] = MessageData(messages[id].text, marker)


def get_messages(context):
    if 'messages' in context.chat_data:
        return context.chat_data['messages']
    return {}


def get_messages_by_marker(context, marker):
    return {k: v for k, v in get_messages(context).items() if v.marker == marker}


def remove_message(context, id):
    messages = get_messages(context)
    if id in messages:
        del messages[id]


def remove_messages_by_marker(context, marker):
    messages = get_messages_by_marker(context, marker)
    for m_id in messages:
        remove_message(context, m_id)
