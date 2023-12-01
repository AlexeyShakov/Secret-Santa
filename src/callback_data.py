from aiogram.filters.callback_data import CallbackData


class BaseButtonClass:
    button_name: str


class GameManageCallBackData(CallbackData, BaseButtonClass):
    ...


class CreationCallBackData(CallbackData, BaseButtonClass):
    ...


class JoinGameCallBackData(CallbackData, BaseButtonClass):
    ...
