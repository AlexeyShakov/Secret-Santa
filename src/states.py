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
