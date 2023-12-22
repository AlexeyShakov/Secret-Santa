from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.callback_data import CreationCallBackData, StartGameCallBack, DeleteGameCallBackData, EditGameCallBackData
from src.callback_data.creator import DisplayPlayersCallBack

creator_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать игру", callback_data=CreationCallBackData(button_name="create_game").pack())],
        [InlineKeyboardButton(text="Изменить количество участников игры", callback_data=EditGameCallBackData(button_name="edit_game").pack())],
        [InlineKeyboardButton(text="Показать присоединившихся участников", callback_data=DisplayPlayersCallBack(button_name="display_players").pack())],
        [InlineKeyboardButton(text="Начать игру", callback_data=StartGameCallBack(button_name="start_game").pack())],
        [InlineKeyboardButton(text="Удалить игру", callback_data=DeleteGameCallBackData(button_name="delete_game").pack())],
    ]
)
