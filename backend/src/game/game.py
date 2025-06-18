"""Clase principal del juego Secret Hitler XL.

Este módulo contiene la implementación principal del juego Secret Hitler XL,
gestionando el estado del juego, las fases y la lógica general del juego.
"""

from random import randint

from src.game.board import GameBoard
from src.game.game_logger import GameLogger, LogLevel
from src.game.game_state import EnhancedGameState
from src.game.phases.setup import SetupPhase
from src.game.powers.abstract_power import PowerOwner
from src.game.powers.power_registry import PowerRegistry
from src.players.player_factory import PlayerFactory
from src.policies.policy_factory import PolicyFactory
from src.roles.role_factory import RoleFactory


class SHXLGame:
    """Clase principal del juego Secret Hitler XL.

    Gestiona la configuración, ejecución y estado del juego Secret Hitler XL.
    """

    def __init__(self, logger=None):
        """Inicializa una nueva instancia del juego.

        Args:
            logger (GameLogger, optional): Logger para registrar eventos del juego.
                Si no se proporciona, se creará uno con nivel NORMAL.
        """
        self.logger = logger if logger else GameLogger(LogLevel.NORMAL)
        self.current_phase = None
        self.state = EnhancedGameState()
        self.communists_in_play = False
        self.anti_policies_in_play = False
        self.emergency_powers_in_play = False
        self.human_player_indices = []
        self.ai_strategy = "role"
        self.player_count = 0
        self.hitler_player = None

        self.was_oktoberfest_active = self.state.oktoberfest_active
        self.old_month = self.state.month_counter

    def setup_game(
        self,
        player_count,
        with_communists=True,
        with_anti_policies=False,
        with_emergency_powers=False,
        human_player_indices=None,
        ai_strategy="role",
    ):
        """Configura el juego con los parámetros dados.

        Args:
            player_count (int): Número de jugadores.
            with_communists (bool): Si incluir la facción comunista.
            with_anti_policies (bool): Si incluir anti-políticas.
            with_emergency_powers (bool): Si incluir poderes de emergencia.
            human_player_indices (list): Lista de índices de jugadores controlados por humanos.
            ai_strategy (str): Estrategia a usar para jugadores IA.
        """
        if with_anti_policies and not with_communists:
            with_anti_policies = False

        self.player_count = player_count
        self.communists_in_play = with_communists
        self.anti_policies_in_play = with_anti_policies
        self.emergency_powers_in_play = with_emergency_powers
        self.human_player_indices = human_player_indices or []
        self.ai_strategy = ai_strategy

        self.state = EnhancedGameState()
        self.state.government_history = []
        self.state.policy_history = []

        self.initialize_board(self.player_count, self.communists_in_play)

        policy_factory = PolicyFactory()
        self.state.board.initialize_policy_deck(
            policy_factory, with_anti_policies, with_emergency_powers
        )

        self.assign_players()
        self.inform_players()
        self.choose_first_president()
        self.logger.log_game_setup(self)

        if self.state.month_counter == 10:
            self.state._start_oktoberfest()

        self.current_phase = SetupPhase(self)
        self.state.set_phase("setup")

    def initialize_board(self, players, communist_flag):
        """Inicializa el tablero del juego.

        Args:
            players (int): Número de jugadores.
            communist_flag (bool): Si están activos los comunistas.
        """
        self.state.board = GameBoard(self.state, players, communist_flag)

    def start_game(self):
        """Ejecuta el juego de principio a fin.

        Returns:
            str: El ganador del juego.
        """
        if self.state.current_phase_name == "setup":
            from src.game.phases.election import ElectionPhase

            self.current_phase = ElectionPhase(self)
            self.state.set_phase("election")

        while not self.state.game_over:
            next_phase = self.current_phase.execute()
            self.current_phase = next_phase

            if isinstance(next_phase, type(self.current_phase)):
                pass
            else:
                new_phase_name = next_phase.__class__.__name__.lower().replace(
                    "phase", ""
                )
                self.state.set_phase(new_phase_name)

        self.state.set_phase("game_over")
        self.logger.log_game_end(self.state.winner, self.state.players, self)
        return self.state.winner

    def get_current_phase_info(self):
        """Obtiene información sobre la fase actual del juego.

        Returns:
            dict: Diccionario con información de la fase actual.
        """
        if not self.current_phase:
            return {
                "name": self.state.current_phase_name,
                "class": "Unknown",
                "can_advance": False,
            }

        phase_class = self.current_phase.__class__.__name__
        phase_name = phase_class.lower().replace("phase", "")

        return {"name": phase_name, "class": phase_class, "can_advance": True}

    def assign_players(self):
        """Crea jugadores y asigna roles.

        Utiliza la fábrica de jugadores para crear jugadores y la fábrica de roles
        para crear y asignar roles a cada jugador.
        """
        player_factory = PlayerFactory()
        player_factory.create_players(
            self.player_count,
            self.state,
            strategy_type=self.ai_strategy,
            human_player_indices=self.human_player_indices or [],
        )

        self.state.active_players = self.state.players.copy()

        role_factory = RoleFactory()
        roles = role_factory.create_roles(
            self.player_count, with_communists=self.communists_in_play
        )

        for i, player in enumerate(self.state.players):
            player.role = roles[i]
            player.initialize_role_attributes()

        self.hitler_player = next(p for p in self.state.players if p.is_hitler)

        player_factory.update_player_strategies(self.state.players, self.ai_strategy)

    def inform_players(self):
        """Informa a los jugadores sobre sus roles y otros jugadores que deben conocer."""
        self._inform_fascists()

        if self.communists_in_play:
            self._inform_communists()

    def _inform_fascists(self):
        """Informa a los fascistas sobre otros fascistas y Hitler."""
        fascists = [p for p in self.state.players if p.is_fascist and not p.is_hitler]

        for fascist in fascists:
            fascist.hitler = self.hitler_player
            fascist.fascists = fascists

        if self.player_count < 8:
            self.hitler_player.fascists = fascists

    def _inform_communists(self):
        """Informa a los comunistas sobre otros comunistas si es aplicable."""
        communists = [p for p in self.state.players if p.is_communist]

        if self.player_count < 11:
            for communist in communists:
                communist.known_communists = [
                    c.id for c in communists if c != communist
                ]

    def choose_first_president(self):
        """Elige el primer presidente aleatoriamente."""
        random_index = randint(0, len(self.state.active_players) - 1)
        chosen_president = self.state.active_players[random_index]

        self.state.president = chosen_president
        self.state.president_candidate = chosen_president

        self.state.chancellor = None
        self.state.chancellor_candidate = None

        if not hasattr(self.state, "government_history"):
            self.state.government_history = []
        if not hasattr(self.state, "previous_government"):
            self.state.previous_government = None

    def set_next_president(self):
        """Establece el próximo presidente basado en la rotación."""
        self.was_oktoberfest_active = self.state.oktoberfest_active
        self.old_month = self.state.month_counter

        self.state.set_next_president()
        self.logger.log_month_change(self)

    def advance_turn(self):
        """Avanza el juego al siguiente turno.

        Incrementa el número de ronda y establece el próximo presidente.
        Se usa principalmente para probar el flujo del juego.

        Returns:
            AbstractPlayer: El candidato a presidente para el próximo turno.
        """
        self.state.round_number += 1
        self.set_next_president()
        return self.state.president_candidate

    def nominate_chancellor(self):
        """Solicita al presidente que nomine un canciller.

        Returns:
            AbstractPlayer: El canciller nominado, o None si no hay candidatos elegibles.
        """
        eligible_chancellors = self.state.get_eligible_chancellors()
        if not eligible_chancellors:
            return None
        return self.state.president_candidate.nominate_chancellor(eligible_chancellors)

    def vote_on_government(self):
        """Solicita a todos los jugadores que voten sobre el gobierno propuesto.

        Returns:
            bool: True si la votación pasó, False en caso contrario.
        """
        self.state.last_votes = []
        for player in self.state.active_players:
            vote = player.vote()
            self.state.last_votes.append(vote)

        ja_votes = sum(1 for vote in self.state.last_votes if vote)
        nein_votes = len(self.state.last_votes) - ja_votes
        vote_passed = ja_votes > nein_votes

        if vote_passed:
            if (
                hasattr(self.state, "president")
                and self.state.president
                and hasattr(self.state, "chancellor")
                and self.state.chancellor
            ):
                self.state.previous_government = {
                    "president": self.state.president.id,
                    "chancellor": self.state.chancellor.id,
                }

            if not hasattr(self.state, "government_history"):
                self.state.government_history = []

            self.state.government_history.append(
                {
                    "president": self.state.president_candidate,
                    "chancellor": self.state.chancellor_candidate,
                    "round": self.state.round_number,
                    "votes": self.state.last_votes,
                }
            )
        else:
            self.state.election_tracker += 1

        self.logger.log_election(
            self.state.president_candidate,
            self.state.chancellor_candidate,
            self.state.last_votes,
            vote_passed,
            self.state.active_players,
        )

        return vote_passed

    def enact_chaos_policy(self):
        """Promulga la política superior automáticamente debido a gobiernos fallidos.

        Returns:
            str: El tipo de política promulgada.
        """
        top_policy = self.state.board.draw_policy(1)[0]
        self.logger.log_chaos(top_policy)
        self.state.board.enact_policy(top_policy, chaos=True)
        self.state.election_tracker = 0
        self.state.enacted_policies += 1
        return top_policy.type

    def check_policy_win(self):
        """Verifica si se ha cumplido una condición de victoria por políticas.

        Returns:
            bool: True si se cumple una condición de victoria por políticas.
        """
        self.logger.log(
            f"\nContadores de políticas - Liberal: {self.state.board.liberal_track}/{self.state.board.liberal_track_size}, Fascista: {self.state.board.fascist_track}/{self.state.board.fascist_track_size}, Comunista: {self.state.board.communist_track}/{self.state.board.communist_track_size}"
        )

        if self.state.board.liberal_track >= self.state.board.liberal_track_size:
            self.state.game_over = True
            self.state.winner = "liberal"
            return True

        if self.state.board.fascist_track >= self.state.board.fascist_track_size:
            self.state.game_over = True
            self.state.winner = "fascist"
            return True

        if (
            self.communists_in_play
            and self.state.board.communist_track_size > 0
            and self.state.board.communist_track
            >= self.state.board.communist_track_size
        ):
            self.state.game_over = True
            self.state.winner = "communist"
            return True

        return False

    def presidential_policy_choice(self, policies):
        """Solicita al presidente que elija políticas.

        Args:
            policies (list): Lista de 3 políticas.

        Returns:
            tuple: (elegidas [2], descartada [1]).
        """
        chosen, discarded = self.state.president.filter_policies(policies)
        self.state.last_discarded = discarded
        self.logger.log_policy_selection(
            self.state.president, chosen, discarded, is_chancellor=False
        )
        return chosen, discarded

    def chancellor_propose_veto(self):
        """Pregunta al canciller si quiere vetar.

        Returns:
            bool: True si se propone veto, False en caso contrario.
        """
        if not self.state.board.veto_available:
            return False
        return self.state.chancellor.veto()

    def president_veto_accepted(self):
        """Pregunta al presidente si acepta el veto.

        Returns:
            bool: True si el veto es aceptado, False en caso contrario.
        """
        return self.state.president.accept_veto()

    def chancellor_policy_choice(self, policies):
        """Solicita al canciller que elija una política.

        Args:
            policies (list): Lista de 2 políticas.

        Returns:
            tuple: (elegida, descartada).
        """
        chosen, discarded = self.state.chancellor.choose_policy(policies)
        self.state.last_discarded = discarded
        self.logger.log_policy_selection(self.state.chancellor, chosen, discarded)
        return chosen, discarded

    def get_fascist_power(self):
        """Obtiene el poder fascista para la posición actual del marcador.

        Returns:
            str or None: El poder a usar, o None si está bloqueado.
        """
        if self.state.block_next_fascist_power:
            self.state.block_next_fascist_power = False
            return None
        return self.state.board.get_power_for_track_position(
            "fascist", self.state.board.fascist_track
        )

    def get_communist_power(self):
        """Obtiene el poder comunista para la posición actual del marcador.

        Returns:
            str or None: El poder a usar, o None si está bloqueado.
        """
        if self.state.block_next_communist_power:
            self.state.block_next_communist_power = False
            return None
        return self.state.board.get_power_for_track_position(
            "communist", self.state.board.communist_track
        )

    def execute_power(self, power_name):
        """Ejecuta un poder.

        Args:
            power_name (str): Nombre del poder.

        Returns:
            Any: Resultado del poder.

        Raises:
            ValueError: Si el propietario del poder es desconocido.
        """
        power_owner = PowerRegistry.get_owner(power_name)

        if power_owner == PowerOwner.PRESIDENT:
            return self.execute_presidential_power(power_name)
        elif power_owner == PowerOwner.CHANCELLOR:
            return self.execute_chancellor_power(power_name)
        else:
            raise ValueError(
                f"Propietario de poder desconocido para el poder: {power_name}"
            )

    def execute_presidential_power(self, power_name):
        """Ejecuta un poder que pertenece al presidente.

        Args:
            power_name (str): Nombre del poder.

        Returns:
            Any: Resultado del poder.
        """
        power = PowerRegistry.get_power(power_name, self)
        power_result = None
        power_target = None

        if power_name in ["chancellor_propaganda", "chancellor_policy_peek"]:
            power_result = power.execute()
            return power_result

        if power_name in ["propaganda", "policy_peek_emergency"]:
            power_result = power.execute()

        elif power_name == "investigate_loyalty":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]
            target = self.state.president.choose_player_to_investigate(eligible_players)
            power_target = target
            power_result = power.execute(target)

        elif power_name == "special_election":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]
            next_president = self.state.president.choose_next_president(
                eligible_players
            )
            power_target = next_president
            power_result = power.execute(next_president)

        elif power_name == "policy_peek":
            power_result = power.execute()

        elif power_name == "execution":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]
            target = self.state.president.kill()
            power_target = target
            power_result = power.execute(target)
            self.logger.log_player_death(target)

        elif power_name == "confession":
            power_result = power.execute()

        elif power_name == "bugging":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]
            target = self.state.president.choose_player_to_bug(eligible_players)
            power_target = target
            power_result = power.execute(target)

        elif power_name == "five_year_plan":
            power_result = power.execute()

        elif power_name == "congress":
            power_result = power.execute()

        elif power_name == "radicalization":
            target = self.state.president.choose_player_to_radicalize()
            power_target = target
            power_result = power.execute(target)

        elif power_name == "impeachment":
            eligible_players = [
                p
                for p in self.state.active_players
                if p.id != self.state.president.id and p.id != self.state.chancellor.id
            ]
            if not eligible_players:
                return None
            revealer = self.state.president.choose_revealer(eligible_players)
            power_target = revealer
            power_result = power.execute(self.state.chancellor, revealer)

        elif power_name == "marked_for_execution":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]
            target = self.state.president.choose_player_to_mark()
            power_target = target
            power_result = power.execute(target)

        elif power_name == "execution_emergency":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]
            target = self.state.president.kill()
            power_target = target
            power_result = power.execute(target)
            self.logger.log_player_death(target)

        elif power_name == "pardon":
            should_pardon = self.state.president.pardon_player()
            if should_pardon:
                power_result = power.execute()
                power_target = power_result
            else:
                self.logger.log(
                    f"El presidente {self.state.president.id} ({self.state.president.name}) eligió no perdonar."
                )

        if power_target or power_result:
            self.logger.log_power_used(
                power_name, self.state.president, power_target, power_result
            )

        return power_result

    def execute_chancellor_power(self, power_name):
        """Ejecuta un poder que pertenece al canciller.

        Args:
            power_name (str): Nombre del poder.

        Returns:
            Any: Resultado del poder.
        """
        power = PowerRegistry.get_power(power_name, self)
        power_result = None
        power_target = None

        if power_name in ["chancellor_propaganda", "chancellor_policy_peek"]:
            power_result = power.execute()

        elif power_name == "chancellor_impeachment":
            eligible_players = [
                p
                for p in self.state.active_players
                if p.id != self.state.president.id and p.id != self.state.chancellor.id
            ]
            if not eligible_players:
                return None
            revealer = self.state.president.choose_revealer(eligible_players)
            power_target = revealer
            power_result = power.execute(revealer)

        elif power_name == "chancellor_marked_for_execution":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.chancellor.id
            ]
            target = self.state.chancellor.choose_player_to_mark()
            power_target = target
            power_result = power.execute(target)

        elif power_name == "chancellor_execution":
            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.chancellor.id
            ]
            target = self.state.chancellor.kill()
            power_target = target
            power_result = power.execute(target)
            self.logger.log_player_death(target)

        elif power_name == "vote_of_no_confidence":
            power_result = power.execute()

        if power_target and power_result:
            self.logger.log_power_used(
                power_name, self.state.chancellor, power_target, power_result
            )

        return power_result
