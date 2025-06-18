"""Almacenamiento global para la API de SHXL.

Este módulo proporciona almacenamiento centralizado para las instancias de juego,
evitando importaciones circulares y manteniendo un registro global de partidas activas.
"""

from typing import Any, Dict

games: Dict[str, Any] = {}


def get_game(game_id):
    """Obtiene un juego por su ID.

    Args:
        game_id: Identificador único del juego.

    Returns:
        Any: Instancia del juego si existe, None en caso contrario.
    """
    return games.get(game_id)


def set_game(game_id, game):
    """Almacena un juego en el registro global.

    Args:
        game_id: Identificador único del juego.
        game: Instancia del juego a almacenar.
    """
    games[game_id] = game


def remove_game(game_id):
    """Elimina un juego del registro global.

    Args:
        game_id: Identificador único del juego a eliminar.
    """
    if game_id in games:
        del games[game_id]


def get_all_games():
    """Obtiene todos los juegos almacenados.

    Returns:
        Dict[str, Any]: Diccionario con todos los juegos indexados por ID.
    """
    return games


def clear_all_games():
    """Limpia todos los juegos del registro.

    Note:
        Útil principalmente para pruebas y reinicio del sistema.
    """
    games.clear()
