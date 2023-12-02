from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from src.callback_data import GameManageCallBackData, CreationCallBackData, JoinGameCallBackData

menu_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Управление игрой",
                                 callback_data=GameManageCallBackData(button_name="manage_game").pack()),
        ],
        [
            InlineKeyboardButton(text="Создание игры",
                                 callback_data=CreationCallBackData(button_name="create_game").pack()),
        ],
        [
            InlineKeyboardButton(text="Присоединиться к игре",
                                 callback_data=JoinGameCallBackData(button_name="join_game").pack()),
        ],
        [InlineKeyboardButton(text="Закрыть", callback_data=JoinGameCallBackData(button_name="Close").pack())],
    ]
)
