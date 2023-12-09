from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


data_to_write = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Введите свои данные"
            )
        ]
    ],
    resize_keyboard=True
)
