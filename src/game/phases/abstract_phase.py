"""Abstract base class for game phases in Secret Hitler XL."""

from abc import ABC, abstractmethod


class GamePhase(ABC):
    """Abstract base class for game phases.

    Game phases represent distinct stages of gameplay (election, legislative, etc.).
    Each phase must implement execute() to define its logic and return the next phase.

    Attributes:
        game: The main game instance containing state and methods.
    """

    def __init__(self, game):
        """Initialize the game phase.

        Args:
            game: The main game instance.
        """
        self.game = game

    @abstractmethod
    def execute(self):
        """Execute the phase logic.

        Returns:
            GamePhase: The next phase to execute.
        """
        pass
