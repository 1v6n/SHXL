from src.game.phases.abstract_phase import GamePhase
from src.game.phases.election import ElectionPhase


class SetupPhase(GamePhase):
    def execute(self):
        """Setup phase execution"""

        return ElectionPhase(self.game)
