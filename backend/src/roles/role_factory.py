"""Fábrica de roles para Secret Hitler XL.

Este módulo proporciona funcionalidades para generar distribuciones de roles
basadas en el número de jugadores y configuración del juego.
"""

from random import shuffle

from src.roles.role import Communist, Fascist, Hitler, Liberal


class RoleFactory:
    """Fábrica para generar roles basados en el número de jugadores y configuración del juego.

    Esta clase proporciona métodos estáticos para crear distribuciones de roles para Secret Hitler XL,
    ajustando dinámicamente el contenido basado en el número de jugadores y configuraciones opcionales.
    """

    @staticmethod
    def get_role_counts(player_count, with_communists=True):
        """Obtiene el número de cada tipo de rol basado en el número de jugadores.

        Args:
            player_count (int): Número de jugadores en el juego.
            with_communists (bool): Si incluir roles comunistas.

        Returns:
            dict: Diccionario con conteos de roles para cada tipo.
        """
        role_distribution = {
            6: {"with_communists": (3, 1, 1), "without_communists": (4, 1, 0)},
            7: {"with_communists": (4, 1, 1), "without_communists": (4, 2, 0)},
            8: {"with_communists": (4, 2, 1), "without_communists": (5, 2, 0)},
            9: {"with_communists": (4, 2, 2), "without_communists": (5, 3, 0)},
            10: {"with_communists": (5, 2, 2), "without_communists": (6, 3, 0)},
            11: {"with_communists": (5, 3, 2), "without_communists": (6, 4, 0)},
            12: {"with_communists": (6, 3, 2), "without_communists": (7, 4, 0)},
            13: {"with_communists": (6, 3, 3), "without_communists": (7, 5, 0)},
            14: {"with_communists": (7, 3, 3), "without_communists": (8, 5, 0)},
            15: {"with_communists": (7, 4, 3), "without_communists": (8, 6, 0)},
            16: {"with_communists": (7, 4, 4), "without_communists": (9, 6, 0)},
        }

        player_count = max(6, min(16, player_count))

        key = "with_communists" if with_communists else "without_communists"
        liberals, fascists, communists = role_distribution[player_count][key]

        return {
            "liberal": liberals,
            "fascist": fascists,
            "communist": communists,
            "hitler": 1,
        }

    @staticmethod
    def create_roles(player_count, with_communists=True):
        """Crea una lista de roles basada en el número de jugadores.

        Args:
            player_count (int): Número de jugadores en el juego.
            with_communists (bool): Si incluir roles comunistas.

        Returns:
            list: Una lista mezclada de instancias de Role distribuidas según las reglas del juego.
        """
        role_counts = RoleFactory.get_role_counts(player_count, with_communists)

        roles = []
        roles.extend([Liberal() for _ in range(role_counts["liberal"])])
        roles.extend([Fascist() for _ in range(role_counts["fascist"])])
        roles.append(Hitler())

        if with_communists:
            roles.extend([Communist() for _ in range(role_counts["communist"])])

        shuffle(roles)

        return roles
