from src.game.phases.abstract_phase import GamePhase
from src.game.phases.election import ElectionPhase


class SetupPhase(GamePhase):
    def execute(self):
        """Setup phase execution"""

        # TODO for now, this is like a halt and can be improved. If self.current_phase = SetupPhase(self) in shxl_game.py is self.current_phase = ElectionPhase(self), the game breaks

        return ElectionPhase(self.game)
