"""Módulo de estrategia base para jugadores de Secret Hitler XL.

Este módulo define la clase abstracta base para todas las estrategias de jugadores,
especificando los métodos que deben implementar las estrategias concretas.
"""

from abc import ABC, abstractmethod


class PlayerStrategy(ABC):
    """Clase base abstracta para estrategias de jugadores.

    Define la interfaz común que deben implementar todas las estrategias
    de jugadores para la toma de decisiones en el juego.
    """

    def __init__(self, player):
        """Inicializa la estrategia con una referencia al jugador.

        Args:
            player: El jugador que utilizará esta estrategia.
        """
        self.player = player

    @abstractmethod
    def nominate_chancellor(self, eligible_players):
        """Elige un canciller de entre los jugadores elegibles.

        Args:
            eligible_players (list): Lista de jugadores que pueden ser cancilleres.

        Returns:
            Player: El jugador elegido como canciller.
        """

    @abstractmethod
    def filter_policies(self, policies):
        """Elige qué políticas pasar como presidente.

        Args:
            policies (list): Lista de políticas disponibles.

        Returns:
            list: Lista de políticas seleccionadas para pasar.
        """

    @abstractmethod
    def choose_policy(self, policies):
        """Elige qué política promulgar como canciller.

        Args:
            policies (list): Lista de políticas disponibles.

        Returns:
            Policy: La política elegida para promulgar.
        """

    @abstractmethod
    def vote(self, president, chancellor):
        """Vota sobre un gobierno propuesto.

        Args:
            president: El presidente propuesto.
            chancellor: El canciller propuesto.

        Returns:
            bool: True para votar ja, False para votar nein.
        """

    @abstractmethod
    def veto(self, policies):
        """Decide si utilizar el poder de veto.

        Args:
            policies (list): Lista de políticas disponibles.

        Returns:
            bool: True para vetar, False para no vetar.
        """

    @abstractmethod
    def accept_veto(self, policies):
        """Decide si aceptar un veto propuesto.

        Args:
            policies (list): Lista de políticas que se quieren vetar.

        Returns:
            bool: True para aceptar el veto, False para rechazarlo.
        """

    @abstractmethod
    def choose_player_to_kill(self, eligible_players):
        """Elige un jugador para ejecutar.

        Args:
            eligible_players (list): Lista de jugadores que pueden ser ejecutados.

        Returns:
            Player: El jugador elegido para la ejecución.
        """

    @abstractmethod
    def choose_player_to_inspect(self, eligible_players):
        """Elige un jugador para inspeccionar.

        Args:
            eligible_players (list): Lista de jugadores que pueden ser inspeccionados.

        Returns:
            Player: El jugador elegido para la inspección.
        """

    @abstractmethod
    def choose_next_president(self, eligible_players):
        """Elige el próximo presidente.

        Args:
            eligible_players (list): Lista de jugadores que pueden ser presidentes.

        Returns:
            Player: El jugador elegido como próximo presidente.
        """

    @abstractmethod
    def choose_player_to_radicalize(self, eligible_players):
        """Elige un jugador para convertir al comunismo.

        Args:
            eligible_players (list): Lista de jugadores que pueden ser radicalizados.

        Returns:
            Player: El jugador elegido para la radicalización.
        """

    @abstractmethod
    def choose_player_to_mark(self, eligible_players):
        """Choose a player to mark for execution"""

    @abstractmethod
    def choose_player_to_bug(self, eligible_players):
        """Choose a player to bug (view party membership)"""

    @abstractmethod
    def propaganda_decision(self, policy):
        """Decide whether to discard the top policy"""

    @abstractmethod
    def choose_revealer(self, eligible_players):
        """Choose a player to reveal party membership to (Impeachment)"""

    @abstractmethod
    def pardon_player(self):
        """Decide whether to pardon a player marked for execution"""

    @abstractmethod
    def chancellor_veto_proposal(self, policies):
        """Decide whether to propose a veto as chancellor"""

    @abstractmethod
    def vote_of_no_confidence(self):
        """Decide whether to enact the discarded policy (Vote of No Confidence)"""

    @abstractmethod
    def social_democratic_removal_choice(self):
        """Choose which policy track to remove from (Social Democratic)"""
