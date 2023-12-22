from aiogram.filters.callback_data import CallbackData


class RegistrationCallBackData(CallbackData, prefix="registration"):
    button_name: str

class EditProfileCallBackData(CallbackData, prefix="edit_profile"):
    button_name: str


class DeleteProfileCallBackData(CallbackData, prefix="delete_profile"):
    button_name: str


class ChangeNameCallBackData(CallbackData, prefix="change_name"):
    button_name: str


class ChangeLastNameCallBackData(CallbackData, prefix="change_last_name"):
    button_name: str
