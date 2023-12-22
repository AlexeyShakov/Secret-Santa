from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.callback_data import JoinGameCallBackData, LeaveGameCallBackData

player_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Вступить в игру", callback_data=JoinGameCallBackData(button_name="join_game").pack())],
        [InlineKeyboardButton(text="Выйти из игры", callback_data=LeaveGameCallBackData(button_name="leave_game").pack())],
    ]
)
