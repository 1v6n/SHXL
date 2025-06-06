from src.game.phases.abstract_phase import GamePhase


class GameOverPhase(GamePhase):
    def execute(self):
        """Game over phase execution"""

        # Reveal all roles
        self.game.state.game_over = True

        return self  # Stays in this state
