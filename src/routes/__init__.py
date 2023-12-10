from .general_routes import general_router
from .player_routes import player_router
from .user_profile_routes import user_profile_router
from .creator_game_routes import creator_game_router


__all__ = ("general_router", "creator_game_router", "player_router", "user_profile_router",)
