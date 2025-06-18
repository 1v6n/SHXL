from src.game.phases.abstract_phase import GamePhase


class GameOverPhase(GamePhase):
    """Fase de fin del juego.

    Esta fase se ejecuta cuando el juego ha terminado por cualquier condición de victoria.
    Se encarga de finalizar el juego, revelar todos los roles y mantener el estado final.
    """

    def execute(self):
        """Ejecuta la fase de fin del juego.

        Marca el juego como terminado y revela toda la información necesaria
        para mostrar el resultado final. Esta fase se mantiene activa
        indefinidamente hasta que se inicie un nuevo juego.

        Returns:
            GameOverPhase: Retorna a sí misma para mantener el estado de fin de juego.
        """
        self.game.state.game_over = True

        return self
