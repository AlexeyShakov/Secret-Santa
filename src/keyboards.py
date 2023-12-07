from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from src.callback_data import GameManageCallBackData, CreationCallBackData, JoinGameCallBackData, \
    RegistrationCallBackData, EditGameCallBackData, DeleteGameCallBackData, StartGameCallBack

menu_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Регистрация",
                callback_data=RegistrationCallBackData(button_name="registration").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Управление игрой",
                callback_data=GameManageCallBackData(button_name="manage_game").pack()
            )
        ]
    ]
)

manage_game_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Создание игры",
                callback_data=CreationCallBackData(button_name="create_game").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Редактировать игру",
                callback_data=EditGameCallBackData(button_name="edit_game").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Присоединиться к игре",
                callback_data=JoinGameCallBackData(button_name="join_game").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Запустить игру",
                callback_data=StartGameCallBack(button_name="start_game").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить игру",
                callback_data=DeleteGameCallBackData(button_name="delete_game").pack()
            )
        ]
    ]
)

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
