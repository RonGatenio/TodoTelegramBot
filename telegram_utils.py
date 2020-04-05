from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def make_inline_keyboard(*buttons):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(button, callback_data=button)
            for button in buttons
        ]]
    )
