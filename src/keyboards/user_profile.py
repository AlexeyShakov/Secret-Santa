from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.callback_data import RegistrationCallBackData, EditProfileCallBackData, DeleteProfileCallBackData, \
    ChangeNameCallBackData, ChangeLastNameCallBackData


manage_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Зарегистрироваться",
                              callback_data=RegistrationCallBackData(button_name="registration").pack())],
        [InlineKeyboardButton(text="Изменить данные профиля",
                              callback_data=EditProfileCallBackData(button_name="edit_profile").pack())],
        [InlineKeyboardButton(text="Удалить профиль",
                              callback_data=DeleteProfileCallBackData(button_name="delete_profile").pack())],

    ]
)


change_name_or_last_name_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Изменить имя", callback_data=ChangeNameCallBackData(button_name="change_name").pack())],
        [InlineKeyboardButton(text="Изменить фамилию", callback_data=ChangeLastNameCallBackData(button_name="change_last_name").pack())],
    ]
)