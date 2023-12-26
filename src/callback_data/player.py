from aiogram.filters.callback_data import CallbackData


class JoinGameCallBackData(CallbackData, prefix="join_game"):
    button_name: str


class LeaveGameCallBackData(CallbackData, prefix="leave_game"):
    button_name: str
