"""Módulo de estado del juego Secret Hitler XL.

Este módulo contiene la implementación del estado mejorado del juego que
soporta todas las características de Secret Hitler XL.
"""

from random import randint


class EnhancedGameState:
    """Estado mejorado del juego para soportar todas las características de SHXL.

    Mantiene el estado completo del juego incluyendo jugadores, votaciones,
    políticas, poderes especiales y condiciones de fin del juego.
    """

    def __init__(self):
        """Inicializa el estado del juego con valores por defecto."""
        self.game_over = False
        self.winner = None
        self.round_number = 0
        self.current_phase_name = "setup"

        self.players = []
        self.active_players = []

        self.president = None
        self.president_candidate = None
        self.chancellor = None
        self.chancellor_candidate = None
        self.election_tracker = 0
        self.last_votes = []
        self.term_limited_players = []

        self.special_election = False
        self.special_election_return_index = None

        self.veto_available = False
        self.last_discarded = None

        self.liberal_track = 0
        self.fascist_track = 0
        self.communist_track = 0

        self.investigated_players = []
        self.known_communists = {}
        self.revealed_affiliations = {}
        self.marked_for_execution = []
        self.enacted_policies = 0
        self.marked_for_execution_tracker = None

        self.block_next_fascist_power = False
        self.block_next_communist_power = False

        self.board = None

        self.most_recent_policy = None
        self.current_policies = []
        self.month_counter = randint(1, 12)
        self.oktoberfest_active = False
        self.original_strategies = {}

        self.month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

    def get_current_month_name(self):
        """Obtiene el nombre del mes actual.

        Returns:
            str: El nombre del mes actual.
        """
        return self.month_names.get(self.month_counter, f"Month {self.month_counter}")

    def set_phase(self, phase_name):
        """Cambia la fase actual del juego.

        Args:
            phase_name (str): Nombre de la nueva fase.
        """
        self.current_phase_name = phase_name

    def get_month_name(self, month_number):
        """Obtiene el nombre de un mes específico.

        Args:
            month_number (int): Número del mes.

        Returns:
            str: El nombre del mes especificado.
        """
        return self.month_names.get(month_number, f"Month {month_number}")

    def reset_election_tracker(self):
        """Reinicia el contador de elecciones a 0."""
        self.election_tracker = 0

    def add_player(self, player):
        """Agrega un jugador al juego.

        Args:
            player (AbstractPlayer): Jugador a agregar.
        """
        self.players.append(player)
        self.active_players.append(player)

    def get_eligible_chancellors(self):
        """Obtiene los jugadores elegibles para ser canciller.

        Returns:
            list: Lista de jugadores elegibles.
        """
        eligible = []

        for player in self.active_players:
            if player == self.president_candidate:
                continue
            if player in self.term_limited_players:
                continue
            if player.is_dead:
                continue
            eligible.append(player)

        return eligible

    def get_next_president_index(self):
        """Obtiene el índice del próximo presidente.

        Returns:
            int: Índice del próximo presidente.
        """
        if self.special_election:
            self.special_election = False
            return (self.special_election_return_index + 1) % len(self.active_players)

        if self.president is None:
            return 0

        try:
            current_index = self.active_players.index(self.president)
            return (current_index + 1) % len(self.active_players)
        except ValueError:
            return 0

    def handle_player_death(self, player):
        """Maneja la muerte de un jugador.

        Args:
            player (AbstractPlayer): El jugador que murió.
        """
        player.is_dead = True

        was_president = player == self.president
        if was_president:
            current_president_index = self.active_players.index(self.president)

        if player in self.active_players:
            self.active_players.remove(player)

        if was_president:
            next_index = (current_president_index) % len(self.active_players)
            self.president_candidate = self.active_players[next_index]
            self.president = None

    def advance_month_counter(self):
        """Avanza el contador de mes y maneja la lógica del Oktober Fest."""
        self.month_counter += 1

        if self.month_counter > 12:
            self.month_counter = 1

        if self.month_counter == 10:
            self._start_oktoberfest()
        elif self.month_counter == 11 and self.oktoberfest_active:
            self._end_oktoberfest()

    def _start_oktoberfest(self):
        """Inicia el Oktober Fest - guarda las estrategias originales y cambia los bots a estrategia aleatoria."""
        if self.oktoberfest_active:
            return

        self.oktoberfest_active = True
        self.original_strategies = {}

        from src.players.strategies.random_strategy import RandomStrategy

        for player in self.active_players:
            if hasattr(player, "is_bot") and player.is_bot:
                self.original_strategies[player.id] = player.strategy
                player.strategy = RandomStrategy(player)

    def _end_oktoberfest(self):
        """Termina el Oktober Fest - restaura las estrategias originales."""
        if not self.oktoberfest_active:
            return

        self.oktoberfest_active = False
        for player in self.active_players:
            if (
                hasattr(player, "is_bot")
                and player.is_bot
                and player.id in self.original_strategies
            ):
                player.strategy = self.original_strategies[player.id]

        self.original_strategies = {}

    def set_next_president(self):
        """Establece el próximo presidente basado en la rotación y avanza el contador de mes."""
        next_index = self.get_next_president_index()
        self.president_candidate = self.active_players[next_index]
        self.advance_month_counter()
