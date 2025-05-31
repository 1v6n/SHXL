# filepath: c:\Users\Admin\Documents\MEGA\Facultad\Materias\IngSoft\test\SHXL\src\players\player_factory.py
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
    """Factory for creating different types of players"""

    @staticmethod
    def create_player(id, name, role, state, strategy_type="smart", player_type="ai"):
        """
        Create a player with the specified role and strategy

        Args:
            id (int): Player ID
            name (str): Player name
            role: Player role
            state: Game state
            strategy_type (str): Type of strategy to use ("random", "role", "smart")
            player_type (str): Type of player to create ("ai" or "human")

        Returns:
            Player: The created player
        """
        if player_type == "human":
            return HumanPlayer(id, name, role, state)

        # Create AI player
        player = AIPlayer(id, name, role, state)

        return player

    def apply_strategy_to_player(self, player, strategy_type="smart"):
        """
        Apply the appropriate strategy to a player based on their role

        Args:
            player: The player to apply the strategy to
            strategy_type (str): Type of strategy to use ("random", "role", "smart")
        """
        # Skip human players
        if not hasattr(player, "strategy"):
            return

        # Apply strategy based on strategy_type
        if strategy_type == "random":
            player.strategy = RandomStrategy(player)

        elif strategy_type == "role":
            # Based on role
            if player.is_fascist or player.is_hitler:
                player.strategy = FascistStrategy(player)
            elif player.is_communist:
                player.strategy = CommunistStrategy(player)
            else:  # Liberal
                player.strategy = LiberalStrategy(player)

        else:  # smart strategy - use the advanced SmartStrategy
            player.strategy = SmartStrategy(player)

    def update_player_strategies(self, players, strategy_type="smart"):
        """
        Update strategies for all players after roles have been assigned

        Args:
            players: List of players to update strategies for
            strategy_type: Strategy type to apply
        """
        for player in players:
            self.apply_strategy_to_player(player, strategy_type)

    def create_players(
        self, count, state, strategy_type="smart", human_player_indices=None
    ):
        """
        Create a list of players

        Args:
            count (int): Number of players to create
            state: Game state
            strategy_type (str): Type of strategy to use for AI players
            human_player_indices (list): List of player indices that should be human-controlled

        Returns:
            list: List of players
        """
        if human_player_indices is None:
            human_player_indices = []

        # Create players
        players = []
        for i in range(count):
            # Determine if this player should be human or AI
            player_type = "human" if i in human_player_indices else "ai"
            name = f"Bot {i}" if player_type == "ai" else f"Player {i}"
            player = self.create_player(
                i, name, None, state, strategy_type, player_type
            )
            players.append(player)

        # Add players to state
        state.players = players

        # Store the strategy type for later application after roles are assigned
        state.ai_strategy_type = strategy_type

        return players
