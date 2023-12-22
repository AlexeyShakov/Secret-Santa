from aiogram.filters.callback_data import CallbackData


class GameManageCallBackData(CallbackData, prefix="manage_game"):
    button_name: str


class CreationCallBackData(CallbackData, prefix="create_game"):
    button_name: str


class JoinGameCallBackData(CallbackData, prefix="join_game"):
    button_name: str


class CloseCallBackData(CallbackData, prefix="close"):
    button_name: str


class RegistrationCallBackData(CallbackData, prefix="registration"):
    button_name: str


class EditGameCallBackData(CallbackData, prefix="edit_game"):
    button_name: str


class DeleteGameCallBackData(CallbackData, prefix="delete_game"):
    button_name: str


class StartGameCallBack(CallbackData, prefix="start_game"):
    button_name: str


class EditProfileCallBackData(CallbackData, prefix="edit_profile"):
    button_name: str


class DeleteProfileCallBackData(CallbackData, prefix="delete_profile"):
    button_name: str


class ChangeNameCallBackData(CallbackData, prefix="change_name"):
    button_name: str


class ChangeLastNameCallBackData(CallbackData, prefix="change_last_name"):
    button_name: str
