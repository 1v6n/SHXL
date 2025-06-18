"""Fábrica de jugadores para Secret Hitler XL.

Este módulo proporciona funcionalidades para crear diferentes tipos de
jugadores con estrategias apropiadas según su rol y configuración.
"""

from src.players.ai_player import AIPlayer
from src.players.human_player import HumanPlayer
from src.players.strategies import (
    CommunistStrategy,
    FascistStrategy,
    LiberalStrategy,
    RandomStrategy,
    SmartStrategy,
)


class PlayerFactory:
    """Fábrica para crear diferentes tipos de jugadores.

    Proporciona métodos estáticos para crear jugadores IA o humanos
    con las estrategias apropiadas según su rol.
    """

    @staticmethod
    def create_player(id, name, role, state, strategy_type="smart", player_type="ai"):
        """Crea un jugador con el rol y estrategia especificados.

        Args:
            id (int): ID del jugador.
            name (str): Nombre del jugador.
            role: Rol del jugador.
            state: Estado del juego.
            strategy_type (str): Tipo de estrategia a usar ("random", "role", "smart").
            player_type (str): Tipo de jugador a crear ("ai" o "human").

        Returns:
            Player: El jugador creado.
        """
        if player_type in ["ai", "bot"]:
            player_type = "ai"
            player = AIPlayer(id, name, role, state)
            player.strategy_type = strategy_type
        else:
            player_type = "human"
            player = HumanPlayer(id, name, role, state)

        player.player_type = player_type
        return player

    @staticmethod
    def apply_strategy_to_player(player, strategy_type="smart"):
        """Aplica la estrategia apropiada a un jugador según su rol.

        Args:
            player: El jugador al que aplicar la estrategia.
            strategy_type (str): Tipo de estrategia a usar ("random", "role", "smart").
        """
        if not hasattr(player, "strategy"):
            return

        if strategy_type == "random":
            player.strategy = RandomStrategy(player)

        elif strategy_type == "role":
            if player.is_fascist or player.is_hitler:
                player.strategy = FascistStrategy(player)
            elif player.is_communist:
                player.strategy = CommunistStrategy(player)
            else:
                player.strategy = LiberalStrategy(player)

        else:
            player.strategy = SmartStrategy(player)

    @staticmethod
    def update_player_strategies(players, strategy_type="smart"):
        """Actualiza las estrategias para todos los jugadores después de asignar roles.

        Args:
            players (list): Lista de jugadores para actualizar estrategias.
            strategy_type (str): Tipo de estrategia a aplicar.
        """
        for player in players:
            PlayerFactory.apply_strategy_to_player(player, strategy_type)

    @staticmethod
    def create_players(count, state, strategy_type="smart", human_player_indices=None):
        """Crea una lista de jugadores.

        Args:
            count (int): Número de jugadores a crear.
            state: Estado del juego.
            strategy_type (str): Tipo de estrategia a usar para jugadores IA.
            human_player_indices (list): Lista de índices de jugadores que serán controlados por humanos.

        Returns:
            list: Lista de jugadores creados.
        """
        if human_player_indices is None:
            human_player_indices = []

        players = []
        for i in range(count):
            player_type = "human" if i in human_player_indices else "ai"
            name = f"Bot {i}" if player_type == "ai" else f"Player {i}"
            player = PlayerFactory.create_player(
                i, name, None, state, strategy_type, player_type
            )
            players.append(player)

        state.players = players
        state.ai_strategy_type = strategy_type

        return players
