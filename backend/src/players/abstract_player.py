"""Módulo de jugador abstracto para Secret Hitler XL.

Este módulo define la clase base abstracta Player que sirve como plantilla
para todos los tipos de jugadores en el juego.
"""

from abc import ABC, abstractmethod


class Player(ABC):
    """Clase abstracta de jugador mejorada para soportar todas las características de SHXL.

    Define la interfaz común para todos los tipos de jugadores, incluyendo
    conocimiento del juego, estado y métodos abstractos que deben implementar
    las clases derivadas.
    """

    def __init__(self, id, name, role, state):
        """Inicializa un jugador con la información básica.

        Args:
            id (int): Identificador único del jugador.
            name (str): Nombre del jugador.
            role: Rol asignado al jugador.
            state: Estado actual del juego.
        """
        self.id = id
        self.name = name
        self.role = role
        self.state = state
        self.is_dead = False
        self.player_count = (
            len(state.players) if hasattr(state, "players") and state.players else 0
        )

        self.hitler = None
        self.fascists = None
        self.known_communists = []
        self.inspected_players = {}
        self.known_affiliations = {}

    @property
    def is_fascist(self):
        """Verifica si el jugador es fascista.

        Returns:
            bool: True si el jugador es fascista, False en caso contrario.
        """
        return self.role.party_membership == "fascist"

    @property
    def is_liberal(self):
        """Verifica si el jugador es liberal.

        Returns:
            bool: True si el jugador es liberal, False en caso contrario.
        """
        return self.role.party_membership == "liberal"

    @property
    def is_communist(self):
        """Verifica si el jugador es comunista.

        Returns:
            bool: True si el jugador es comunista, False en caso contrario.
        """
        return self.role.party_membership == "communist"

    @property
    def is_hitler(self):
        """Verifica si el jugador es Hitler.

        Returns:
            bool: True si el jugador es Hitler, False en caso contrario.
        """
        return self.role.role == "hitler"

    @property
    def knows_hitler(self):
        """Verifica si el jugador conoce quién es Hitler.

        Returns:
            bool: True si el jugador conoce la identidad de Hitler.
        """
        return self.hitler is not None

    def __repr__(self):
        """Devuelve una representación en cadena del jugador.

        Returns:
            str: Representación del jugador con id, nombre y rol.
        """
        return f"Player id:{self.id}, name:{self.name}, role:{self.role}"

    def initialize_role_attributes(self):
        """Inicializa atributos basados en el rol asignado.

        Configura el conocimiento inicial del jugador según su rol,
        incluyendo información sobre otros fascistas, Hitler o comunistas.
        """
        if self.role is None:
            return

        player_count = (
            len(self.state.players)
            if hasattr(self.state, "players") and self.state.players
            else 0
        )

        if self.is_fascist and not self.is_hitler:
            self.fascists = []
            self.hitler = None
        elif self.is_hitler and player_count < 8:
            self.fascists = []
        elif self.is_communist and player_count < 11:
            self.known_communists = []

    @abstractmethod
    def nominate_chancellor(self):
        """Elige un canciller.

        Returns:
            Player: El canciller nominado.
        """

    @abstractmethod
    def filter_policies(self, policies):
        """Elige qué políticas pasar como presidente.

        Args:
            policies (list): Lista de 3 políticas.

        Returns:
            tuple: (políticas elegidas [2], política descartada [1]).
        """

    @abstractmethod
    def choose_policy(self, policies):
        """Elige qué política promulgar como canciller.

        Args:
            policies (list): Lista de 2 políticas.

        Returns:
            tuple: (política elegida [1], política descartada [1]).
        """

    @abstractmethod
    def vote(self):
        """Vota sobre un gobierno.

        Returns:
            bool: True para Ja, False para Nein.
        """

    @abstractmethod
    def veto(self):
        """Decide si vetar como canciller.

        Returns:
            bool: True para vetar, False en caso contrario.
        """

    @abstractmethod
    def accept_veto(self):
        """Decide si aceptar el veto como presidente.

        Returns:
            bool: True para aceptar el veto, False en caso contrario.
        """

    @abstractmethod
    def view_policies(self, policies):
        """Reacciona a ver políticas con espionaje de políticas.

        Args:
            policies (list): Lista de políticas vistas.
        """

    @abstractmethod
    def kill(self):
        """Elige un jugador para ejecutar.

        Returns:
            Player: El jugador elegido para ejecutar.
        """

    @abstractmethod
    def choose_player_to_mark(self):
        """Elige un jugador para marcar.

        Returns:
            Player: El jugador elegido para marcar.
        """

    @abstractmethod
    def inspect_player(self):
        """Elige un jugador para inspeccionar.

        Returns:
            Player: El jugador elegido para inspeccionar.
        """

    @abstractmethod
    def choose_next(self):
        """Elige el próximo presidente en elección especial.

        Returns:
            Player: El jugador elegido como próximo presidente."""

    @abstractmethod
    def choose_player_to_radicalize(self):
        """Elige un jugador para convertir al comunismo.

        Returns:
            Player: El jugador elegido para radicalizar.
        """

    @abstractmethod
    def propaganda_decision(self, policy):
        """Decide si descartar la política superior.

        Args:
            policy: La política superior del mazo.

        Returns:
            bool: True para descartar, False para mantener.
        """

    @abstractmethod
    def choose_revealer(self, eligible_players):
        """Elige un jugador para revelar afiliación política.

        Args:
            eligible_players (list): Jugadores elegibles.

        Returns:
            Player: El jugador elegido para revelar afiliación.
        """

    @abstractmethod
    def social_democratic_removal_choice(self, state):
        """Elige qué pista de políticas eliminar (Socialdemócrata).

        Args:
            state: Estado actual del juego.

        Returns:
            str: "fascist" o "communist".
        """
