from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


data_to_write = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отменить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
