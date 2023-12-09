from .general_routes import general_router
from .create_routes import create_router
from .join_game_routes import join_game_router
from .registration_routes import registration_router
from .start_game_routes import start_game_router


__all__ = ("general_router", "create_router", "join_game_router", "registration_router", "start_game_router")
