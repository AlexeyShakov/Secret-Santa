from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    name = State()
    last_name = State()


class CreationGameState(StatesGroup):
    player_number = State()


class JoinGameState(StatesGroup):
    game_name = State()


class StartGameState(StatesGroup):
    game_name = State()


class DeleteProfileState(StatesGroup):
    answer = State()


class ChangeNameState(StatesGroup):
    name = State()


class ChangeLastNameState(StatesGroup):
    last_name = State()


class DeleteGameState(StatesGroup):
    game_name = State()


class DisplayConnectedPlayersState(StatesGroup):
    game_name = State()


class ChangePlayersNumberState(StatesGroup):
    game_name = State()
    new_players_number = State()


class LeaveGameState(StatesGroup):
    game_name = State()


class AddReviewState(StatesGroup):
    review = State()
