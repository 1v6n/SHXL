"""
Global storage for SHXL API
Centralized storage to avoid circular imports
"""

from typing import Any, Dict

games: Dict[str, Any] = {}


def get_game(game_id):
    """Get a game by ID"""
    return games.get(game_id)


def set_game(game_id, game):
    """Store a game"""
    games[game_id] = game


def remove_game(game_id):
    """Remove a game"""
    if game_id in games:
        del games[game_id]


def get_all_games():
    """Get all games"""
    return games


def clear_all_games():
    """Clear all games (useful for testing)"""
    games.clear()
