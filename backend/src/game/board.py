"""Módulo del tablero del juego Secret Hitler XL.

Este módulo contiene la implementación del tablero del juego, incluyendo
los contadores de políticas, poderes y la lógica de victoria.
"""

from random import shuffle

from src.game.game_logger import GameLogger, LogLevel
from src.game.powers.power_registry import PowerRegistry

VETO_POWER_THRESHOLD = 5


class GameBoard:
    """Representa el tablero del juego con contadores de políticas y poderes.

    Gestiona los contadores de políticas liberales, fascistas y comunistas,
    así como los poderes desbloqueados y las condiciones de victoria.
    """

    def __init__(self, game_state, player_count, with_communists=True, logger=None):
        """Inicializa el tablero del juego.

        Args:
            game_state: Estado del juego.
            player_count (int): Número de jugadores.
            with_communists (bool): Si los comunistas están en juego.
            logger (GameLogger, optional): Logger para registrar eventos.
        """
        self.state = game_state
        self.logger = logger or GameLogger(LogLevel.NORMAL)
        self.player_count = player_count
        self.with_communists = with_communists

        self.liberal_track_size = 5
        self.fascist_track_size = 6
        self.communist_track_size = self._get_communist_track_size()

        self.liberal_track = 0
        self.fascist_track = 0
        self.communist_track = 0

        self.policies = []
        self.discards = []

        self.fascist_powers = self._setup_fascist_powers()
        self.communist_powers = self._setup_communist_powers()

        self.veto_available = False

    def _get_communist_track_size(self):
        """Determina el tamaño del marcador comunista basado en el número de jugadores.

        Returns:
            int: Tamaño del marcador comunista (0 si no hay comunistas).
        """
        if not self.with_communists:
            return 0

        if self.player_count < 9:
            return 5
        else:
            return 6

    def _setup_fascist_powers(self):
        """Configura los espacios de poder fascista basado en el número de jugadores.

        Returns:
            list: Lista de poderes fascistas para cada posición del marcador.
        """
        if self.player_count < 8:
            return [None, None, "policy_peek", "execution", "execution"]

        elif self.player_count < 11:
            return [
                None,
                "investigate_loyalty",
                "special_election",
                "execution",
                "execution",
            ]

        else:
            return [
                "investigate_loyalty",
                "investigate_loyalty",
                "special_election",
                "execution",
                "execution",
            ]

    def _setup_communist_powers(self):
        """Configura los espacios de poder comunista basado en el número de jugadores.

        Returns:
            list: Lista de poderes comunistas para cada posición del marcador.
        """
        if not self.with_communists:
            return []

        if self.player_count < 9:
            return ["bugging", "radicalization", "five_year_plan", "congress"]

        elif self.player_count < 11:
            return [
                "bugging",
                "radicalization",
                "five_year_plan",
                "congress",
                "confession",
            ]

        else:
            return [
                None,
                "radicalization",
                "five_year_plan",
                "radicalization",
                "confession",
            ]

    def initialize_policy_deck(
        self, policy_factory, with_anti_policies=False, with_emergency=False
    ):
        """Inicializa el mazo de políticas con las cartas apropiadas.

        Args:
            policy_factory: Fábrica para crear políticas.
            with_anti_policies (bool): Si incluir anti-políticas.
            with_emergency (bool): Si incluir poderes de emergencia.
        """
        self.policies = policy_factory.create_policy_deck(
            self.player_count, self.with_communists, with_anti_policies, with_emergency
        )
        self.discards = []

    def draw_policy(self, count=1):
        """Extrae políticas del mazo.

        Args:
            count (int): Número de políticas a extraer.

        Returns:
            list: Lista de políticas extraídas.
        """
        self.logger.log_policy_deck(self.policies)

        if len(self.policies) < count:
            self.policies.extend(self.discards)
            self.discards = []
            shuffle(self.policies)
            self.logger.log_shuffle(self.policies)

        drawn = []
        for _ in range(count):
            drawn.append(self.policies.pop(0))

        if count > 1:
            self.logger.log_drawn_policies(drawn)

        return drawn

    def discard(self, policies):
        """Descarta políticas al montón de descarte.

        Args:
            policies: Una política o lista de políticas a descartar.
        """
        if not isinstance(policies, list):
            policies = [policies]

        self.discards.extend(policies)

    def enact_policy(self, policy, chaos=False, emergency=False, antipolicies=False):
        """Promulga una política en el marcador apropiado.

        Args:
            policy: La política a promulgar.
            chaos (bool): Si es promulgada por caos.
            emergency (bool): Si incluye poderes de emergencia.
            antipolicies (bool): Si incluye anti-políticas.

        Returns:
            str or None: Poder presidencial otorgado por esta política, si existe.
        """
        policy_type = policy.type
        power = None

        if policy_type == "liberal":
            self.liberal_track += 1
            if self.liberal_track >= self.liberal_track_size:
                self.state.game_over = True
                self.state.winner = "liberal"

        elif policy_type == "fascist":
            self.fascist_track += 1
            self.state.fascist_track = self.fascist_track

            power = self.get_fascist_power() if not chaos else None

            if self.fascist_track >= self.fascist_track_size:
                self.state.game_over = True
                self.state.winner = "fascist"

            if self.fascist_track >= VETO_POWER_THRESHOLD:
                self.veto_available = True

        elif policy_type == "communist":
            self.communist_track += 1
            self.state.communist_track = self.communist_track

            power = self.get_communist_power() if not chaos else None

            if (
                self.communist_track >= self.communist_track_size
                and self.communist_track_size > 0
            ):
                self.state.game_over = True
                self.state.winner = "communist"

        if antipolicies is True:
            if policy_type == "antifascist":
                self.communist_track += 1

                if self.fascist_track > 0:
                    self.fascist_track -= 1
                    self.state.fascist_track = self.fascist_track

                    if self.fascist_track < VETO_POWER_THRESHOLD:
                        self.veto_available = False

                self.state.block_next_fascist_power = True

            elif policy_type == "anticommunist":
                self.fascist_track += 1
                self.state.fascist_track = self.fascist_track

                if self.communist_track > 0:
                    self.communist_track -= 1

                self.state.block_next_communist_power = True

            elif policy_type == "socialdemocratic":
                self.liberal_track += 1

                remove = self.state.chancellor.social_democratic_removal_choice(
                    self.state
                )

                if remove == "fascist":
                    if self.fascist_track > 0:
                        self.fascist_track -= 1

                    self.state.fascist_track = self.fascist_track

                    if self.fascist_track < VETO_POWER_THRESHOLD:
                        self.veto_available = False

                    self.state.block_next_fascist_power = True

                else:
                    if self.communist_track > 0:
                        self.communist_track -= 1

                    self.state.block_next_communist_power = True

        if emergency is True:
            if policy_type == "article48":
                power = PowerRegistry.get_article48_power()
                print(
                    f"President {self.state.president.name} executed Article 48 powers."
                )

            elif policy_type == "enablingact":
                power = PowerRegistry.get_enabling_act_power()
                print(
                    f"Chancellor {self.state.chancellor.name} executed Enabling Act powers."
                )

        self.state.most_recent_policy = policy

        if not hasattr(self.state, "policy_history"):
            self.state.policy_history = []

        self.state.policy_history.append(
            {
                "policy": policy_type,
                "president": self.state.president,
                "chancellor": self.state.chancellor,
                "round": self.state.round_number,
                "liberal_track": self.state.board.liberal_track,
                "fascist_track": self.state.board.fascist_track,
                "communist_track": (
                    self.communist_track if self.with_communists else 0
                ),
            }
        )

        self.state.enacted_policies += 1

        return power

    def get_fascist_power(self):
        """Obtiene el poder fascista para la posición actual del marcador.

        Returns:
            str or None: El poder a usar.
        """
        if self.state.block_next_fascist_power:
            self.state.block_next_fascist_power = False
            return None

        return self.get_power_for_track_position(
            "fascist", self.state.board.fascist_track
        )

    def get_communist_power(self):
        """Obtiene el poder comunista para la posición actual del marcador.

        Returns:
            str or None: El poder a usar.
        """
        if self.state.block_next_communist_power:
            self.state.block_next_communist_power = False
            return None

        return self.get_power_for_track_position(
            "communist", self.state.board.communist_track
        )

    def get_power_for_track_position(self, track_type, position):
        """Obtiene el poder en una posición específica de un marcador.

        Args:
            track_type (str): El tipo de marcador ("fascist" o "communist").
            position (int): La posición en el marcador (indexado desde 1).

        Returns:
            str or None: El poder en esa posición.
        """
        if track_type == "fascist":
            if 1 <= position <= len(self.fascist_powers):
                return self.fascist_powers[position - 1]

        elif track_type == "communist":
            if 1 <= position <= len(self.communist_powers):
                return self.communist_powers[position - 1]

        return None
