from aiogram.filters.callback_data import CallbackData


class GameManageCallBackData(CallbackData, prefix="manage_game"):
    button_name: str


class CreationCallBackData(CallbackData, prefix="create_game"):
    button_name: str


class CloseCallBackData(CallbackData, prefix="close"):
    button_name: str


class EditGameCallBackData(CallbackData, prefix="edit_game"):
    button_name: str


class DeleteGameCallBackData(CallbackData, prefix="delete_game"):
    button_name: str


class StartGameCallBack(CallbackData, prefix="start_game"):
    button_name: str


class DisplayPlayersCallBack(CallbackData, prefix="display_players"):
    button_name: str
