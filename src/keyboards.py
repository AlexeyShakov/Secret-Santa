from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


data_to_write = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Эту кнопку не нажимать!"
            )
        ]
    ],
    resize_keyboard=True
)
