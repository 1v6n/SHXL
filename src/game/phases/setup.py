from src.game.phases.abstract_phase import GamePhase
from src.game.phases.election import ElectionPhase


class SetupPhase(GamePhase):
    """Fase de configuración del juego.

    Esta fase se encarga de la configuración inicial del juego antes de comenzar
    las rondas de elecciones. Una vez completada la configuración, transiciona
    automáticamente a la fase de elección.
    """

    def execute(self):
        """Ejecuta la fase de configuración.

        Realiza todas las tareas necesarias para configurar el estado inicial
        del juego y luego transiciona a la fase de elección para comenzar
        el juego propiamente dicho.

        Returns:
            ElectionPhase: La siguiente fase del juego (fase de elección).
        """
        return ElectionPhase(self.game)
