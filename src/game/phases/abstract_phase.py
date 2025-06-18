"""Clase base abstracta para las fases del juego en Secret Hitler XL.

Este módulo define la interfaz común que deben implementar todas las fases
del juego como elección, legislativa, y fin de juego.
"""

from abc import ABC, abstractmethod


class GamePhase(ABC):
    """Clase base abstracta para las fases del juego.

    Las fases del juego representan etapas distintas de la jugabilidad como
    elección, legislativa, etc. Cada fase debe implementar execute() para
    definir su lógica y retornar la siguiente fase.

    Attributes:
        game: Instancia principal del juego que contiene estado y métodos.
    """

    def __init__(self, game):
        """Inicializa la fase del juego.

        Args:
            game: Instancia principal del juego.
        """
        self.game = game

    @abstractmethod
    def execute(self):
        """Ejecuta la lógica de la fase.

        Returns:
            GamePhase: La siguiente fase a ejecutar.
        """
        pass
