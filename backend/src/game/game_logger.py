"""Módulo de logging para el juego Secret Hitler XL.

Este módulo proporciona funcionalidades de logging para registrar eventos
del juego con diferentes niveles de detalle.
"""

import logging
from enum import Enum, auto


class LogLevel(Enum):
    """Enumeración para los niveles de logging.

    Define los diferentes niveles de detalle para el logging del juego.
    """

    NONE = auto()
    MINIMAL = auto()
    NORMAL = auto()
    VERBOSE = auto()
    DEBUG = auto()


class GameLogger:
    """Logger para eventos del juego.

    Maneja el logging de eventos del juego con diferentes niveles de detalle
    y mantiene estadísticas del juego.
    """

    def __init__(self, level=LogLevel.NORMAL):
        """Inicializa el logger con el nivel especificado.

        Args:
            level (LogLevel): Nivel de detalle del logging.
        """
        self.level = level

        logging.basicConfig(level=logging.INFO, format="%(message)s")
        self.logger = logging.getLogger("SHXL")

        self.policy_stats = {
            "liberal": 0,
            "fascist": 0,
            "communist": 0,
            "anti-liberal": 0,
            "anti-fascist": 0,
            "anti-communist": 0,
        }

        self.election_count = 0

        self.failed_elections = 0

    def log(self, message, level=LogLevel.NORMAL):
        """Registra un mensaje si el nivel de log actual es suficientemente alto.

        Args:
            message (str): Mensaje a registrar.
            level (LogLevel): Nivel de este mensaje.
        """
        if level.value <= self.level.value:
            self.logger.info(message)

    def log_game_setup(self, game, level=LogLevel.NORMAL):
        """Registra la información de configuración del juego.

        Args:
            game: El objeto del juego.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== GAME SETUP =====\n")
        self.logger.info("Players: %d", game.player_count)

        if (
            hasattr(game.state, "players")
            and game.state.players
            and game.state.players[0].role is not None
        ):
            self.logger.info(
                "Liberals: %d", sum(1 for p in game.state.players if p.is_liberal)
            )
            self.logger.info(
                "Fascists: %d",
                sum(1 for p in game.state.players if p.is_fascist and not p.is_hitler),
            )
            self.logger.info(
                "Hitler: %d", sum(1 for p in game.state.players if p.is_hitler)
            )
            if game.communists_in_play:
                self.logger.info(
                    "Communists: %d",
                    sum(1 for p in game.state.players if p.is_communist),
                )

        self.logger.info(
            "Communists: %s", "Enabled" if game.communists_in_play else "Disabled"
        )
        self.logger.info(
            "Anti-policies: %s", "Enabled" if game.anti_policies_in_play else "Disabled"
        )
        self.logger.info(
            "Emergency powers: %s",
            "Enabled" if game.emergency_powers_in_play else "Disabled",
        )

        self.logger.info("Liberal track size: %d", game.state.board.liberal_track_size)
        self.logger.info("Fascist track size: %d", game.state.board.fascist_track_size)
        if game.communists_in_play:
            self.logger.info(
                "Communist track size: %d", game.state.board.communist_track_size
            )

        self.logger.info(
            "\n🗓️ The game begins in %s!", game.state.get_current_month_name()
        )

        if game.state.month_counter == 10:
            self.logger.info(
                "🍺 Starting in October - Oktober Fest is active from the beginning! All bots will use random strategy! 🍺"
            )

    def log_player_roles(self, players, level=LogLevel.DEBUG):
        """Registra los roles de los jugadores (solo debug - muestra información oculta).

        Args:
            players (list): Lista de jugadores.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("===== PLAYER ROLES =====")
        for player in players:
            if player.is_hitler:
                self.logger.info(
                    "Player %d (%s): %s (Hitler)",
                    player.id,
                    player.name,
                    player.role,
                )
            elif player.role.role and player.role.role != "regular":
                self.logger.info(
                    "Player %d (%s): %s (%s)",
                    player.id,
                    player.name,
                    player.role,
                    player.role.role,
                )
            else:
                self.logger.info(
                    "Player %d (%s): %s",
                    player.id,
                    player.name,
                    player.role,
                )

    def log_election(
        self,
        president,
        chancellor,
        votes,
        result,
        active_players=None,
        level=LogLevel.NORMAL,
    ):
        """Registra los resultados de las elecciones.

        Args:
            president: Candidato a presidente.
            chancellor: Candidato a canciller.
            votes (list): Lista de votos.
            result (bool): Si la votación pasó.
            active_players (list, optional): Lista de jugadores activos.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        self.election_count += 1
        if not result:
            self.failed_elections += 1

        if level.value > self.level.value:
            return

        ja_votes = sum(1 for v in votes if v)
        nein_votes = len(votes) - ja_votes

        self.logger.info("\n===== ELECTION =====\n")
        self.logger.info("Election #%d", self.election_count)

        president_info = f"President candidate: {president.name}"
        if self.level.value == LogLevel.DEBUG.value:
            president_info += f" [{president.role.party_membership}"
            if president.is_hitler:
                president_info += "/Hitler"
            president_info += "]"
        self.logger.info(president_info)

        if chancellor is not None:
            chancellor_info = f"Chancellor candidate: {chancellor.name}"
            if self.level.value == LogLevel.DEBUG.value:
                chancellor_info += f" [{chancellor.role.party_membership}"
                if chancellor.is_hitler:
                    chancellor_info += "/Hitler"
                chancellor_info += "]"
            self.logger.info(chancellor_info)
        else:
            self.logger.info("Chancellor candidate: None")

        self.logger.info("Votes: %d Ja, %d Nein", ja_votes, nein_votes)
        self.logger.info("Individual votes:")
        if active_players:
            for player, vote in zip(active_players, votes):
                self.logger.info("  Player %d: %s", player.id, "Ja" if vote else "Nein")

        self.logger.info("Result: %s", "Passed" if result else "Failed")

    def log_drawn_policies(self, policies, level=LogLevel.DEBUG):
        """Registra las políticas extraídas (solo debug - muestra información oculta).

        Args:
            policies (list): Lista de políticas extraídas.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== DRAWN POLICIES =====\n")
        self.logger.info("Policies drawn: %s", ", ".join(p.type for p in policies))

    def log_policy_selection(
        self,
        politic,
        chosen,
        discarded,
        is_chancellor=True,
        level=LogLevel.DEBUG,
    ):
        """Registra la selección de políticas del político (solo debug - muestra información oculta).

        Args:
            politic: Jugador presidente o canciller.
            chosen: Políticas/política que fueron elegidas.
            discarded: Políticas/política que fueron descartadas.
            is_chancellor (bool): Si es el canciller quien selecciona.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            if is_chancellor:
                self.logger.info(
                    "Chancellor %s enacted a %s policy",
                    politic.name,
                    chosen.type,
                )
            return

        if is_chancellor:
            self.logger.info(
                "Chancellor %s enacted a %s policy and discarded a %s policy",
                politic.name,
                chosen.type,
                discarded.type,
            )
        else:
            self.logger.info(
                "President %s prioritized %s and %s and discarded the %s policy",
                politic.name,
                chosen,
                discarded,
                discarded.type,
            )

    def log_policy_enacted(
        self, policy, track_position, power=None, level=LogLevel.NORMAL
    ):
        """Registra la promulgación de una política.

        Args:
            policy: Política promulgada.
            track_position (int): Posición en el marcador.
            power (str, optional): Poder otorgado.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.policy_stats[policy.type] += 1

        self.logger.info("===== POLICY ENACTED =====")
        self.logger.info("Policy enacted: %s", policy.type)
        self.logger.info("Track position: %d", track_position)

        if power:
            self.logger.info("Power granted: %s", power)

        if self.level.value >= LogLevel.NORMAL.value:
            self.logger.info("Current policy statistics:")
            for policy_type, count in self.policy_stats.items():
                if count > 0:
                    self.logger.info("  %s: %d", policy_type, count)

    def log_power_used(
        self,
        power,
        politic,
        target=None,
        result=None,
        is_president=True,
        level=LogLevel.NORMAL,
    ):
        """Registra el uso de un poder presidencial o cancilleril.

        Args:
            power (str): Poder utilizado.
            politic: Político (presidente o canciller) que usa el poder.
            target: Objetivo del poder (opcional).
            result: Resultado del poder (opcional).
            is_president (bool): Si es el presidente quien usa el poder.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return self.logger.info("\n===== POWER USED =====\n")

        if is_president:
            politic_info = f"President: {politic.name}"
        else:
            politic_info = f"Chancellor: {politic.name}"

        if self.level.value == LogLevel.DEBUG.value:
            politic_info += f" [{politic.role.party_membership}]"

        self.logger.info(politic_info)
        self.logger.info("Power: %s", power)

        if target:
            target_info = f"Target: {target.name}"
            if self.level.value == LogLevel.DEBUG.value:
                target_info += f" [{target.role.party_membership}"
                if target.is_hitler:
                    target_info += "/Hitler"
                target_info += "]"
            self.logger.info(target_info)

        if result:
            if isinstance(result, str):
                self.logger.info("Result: %s", result)
            elif power == "investigate_loyalty" or power == "bugging":
                self.logger.info("Party membership: %s", result)
            elif power == "policy_peek":
                self.logger.info("Top policies: %s", ", ".join(p.type for p in result))
            elif power == "execution":
                hitler_info = " (Hitler was executed!)" if result.is_hitler else ""
                self.logger.info("Player %d was executed%s", result.id, hitler_info)
            elif power == "radicalization":
                self.logger.info("Player %d was converted to Communist", result.id)

    def log_anti_policy_usage(self, policy_type, player, level=LogLevel.NORMAL):
        """Registra el uso de una anti-política.

        Args:
            policy_type (str): Tipo de anti-política usada.
            player: El jugador que la usó.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== ANTI-POLICY USED =====\n")
        self.logger.info("Player %d (%s) used %s", player.id, player.name, policy_type)

    def log_emergency_power_usage(self, power_name, player):
        """Registra el uso de un poder de emergencia.

        Args:
            power_name (str): Nombre del poder de emergencia.
            player: El jugador que lo usó.
        """
        if self.level.value < LogLevel.NORMAL.value:
            return

        self.logger.info("\n===== EMERGENCY POWER =====\n")
        self.logger.info("%s used %s", player.name, power_name)
        self.logger.info("\n===========================\n")

    def log_game_end(self, winner, players, game):
        """Registra el final del juego y revela los roles.

        Args:
            winner (str): Equipo ganador.
            players (list): Lista de jugadores.
            game: Instancia del juego.
        """

        self.logger.info("\n===== ROLE REVEALS =====\n")

        liberals = []
        fascists = []
        hitler = None
        communists = []

        for player in players:

            if player.is_hitler:

                hitler = player

            elif player.is_fascist:

                fascists.append(player)

            elif player.is_communist:

                communists.append(player)
            elif player.is_liberal:
                liberals.append(player)

        self.logger.info("Liberal team:")
        for player in liberals:
            status = "Dead" if player.is_dead else "Alive"
            self.logger.info("%s: %s", player.name, status)

        self.logger.info("\nFascist team:")
        if hitler:
            self.logger.info(
                "%s - Hitler: %s",
                hitler.name,
                "Dead" if hitler.is_dead else "Alive",
            )
        else:
            self.logger.info("Hitler: Not found/assigned")
        for player in fascists:
            status = "Dead" if player.is_dead else "Alive"
            self.logger.info("%s: %s", player.name, status)

        if game.communists_in_play:
            self.logger.info("\nCommunist team:")
            for player in communists:
                status = "Dead" if player.is_dead else "Alive"
                self.logger.info("%s: %s", player.name, status)

        self.logger.info("\n===== GAME OVER =====\n")
        self.logger.info("Winner: %s", winner)

        if game.state.winner == "liberal":
            if hitler and hitler.is_dead:
                self.logger.info("Hitler was executed!")
            else:
                self.logger.info(
                    "Liberals passed %d liberal policies!",
                    game.state.board.liberal_track_size,
                )

        elif game.state.winner == "fascist":
            if game.state.fascist_track >= game.state.board.fascist_track_size:
                self.logger.info(
                    "Fascists passed %d fascist policies!",
                    game.state.board.fascist_track_size,
                )
            else:
                self.logger.info(
                    "Hitler was elected Chancellor after 3 fascist policies!"
                )

        elif game.state.winner == "communist":
            self.logger.info(
                "Communists passed %d communist policies!",
                game.state.board.communist_track_size,
            )

        elif game.state.winner == "liberals_and_communists":
            self.logger.info("Hitler was executed by a communist president!")

        self.logger.info("Total elections: %d", self.election_count)
        self.logger.info("Failed elections: %d", self.failed_elections)
        self.logger.info("Policies enacted: %s\n", game.state.enacted_policies)

    def log_game_state(self, game, level=LogLevel.VERBOSE):
        """Registra el estado actual del juego.

        Args:
            game: Instancia del juego.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== GAME STATE =====\n")

        self.logger.info("Round: %d", game.state.round_number)

        self.logger.info(
            "Liberal policies: %d/%d",
            game.state.board.liberal_track,
            game.state.board.liberal_track_size,
        )

        self.logger.info(
            "Fascist policies: %d/%d",
            game.state.board.fascist_track,
            game.state.board.fascist_track_size,
        )

        if game.communists_in_play:
            self.logger.info(
                "Communist policies: %d/%d",
                game.state.board.communist_track,
                game.state.board.communist_track_size,
            )

        self.logger.info("Election tracker: %d/3", game.state.election_tracker)
        self.logger.info(
            "Veto power: %s",
            "Available" if game.state.veto_available else "Not available",
        )

        active_player_info = "Active players: "
        active_player_info += ", ".join(
            [f"Player {p.id}" for p in game.state.active_players]
        )
        self.logger.info(active_player_info)

        dead_players = [p for p in game.state.players if p.is_dead]
        if dead_players:
            dead_player_info = "Dead players: "
            dead_player_info += ", ".join([f"Player {p.id}" for p in dead_players])
            self.logger.info(dead_player_info)

        if level.value == LogLevel.DEBUG.value:
            self.logger.info("Policies in deck: %d", len(game.state.board.policies))
            self.logger.info("Policies in discard: %d", len(game.state.board.discards))

    def log_player_death(self, player, level=LogLevel.NORMAL):
        """Registra la muerte de un jugador.

        Args:
            player: Jugador que murió.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== PLAYER DEATH =====\n")

        self.logger.info("Player %s has been executed", player.name)

    def log_chaos(self, policy, level=LogLevel.NORMAL):
        """Registra la promulgación de una política por caos.

        Args:
            policy: Política promulgada debido al caos.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== CHAOS =====\n")

        self.logger.info("Chaos policy enacted: %s", policy.type)

        self.logger.info("Presidential power not activated")

        self.logger.info("Term limits lifted for next election")

    def log_policy_deck(self, policies, level=LogLevel.DEBUG):
        """Registra el contenido del mazo de políticas.

        Args:
            policies (list): Lista de políticas en el mazo.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== POLICY DECK =====\n")
        self.logger.info("Policies in deck: %s", policies)

    def log_shuffle(self, policies, level=LogLevel.DEBUG):
        """Registra la mezcla del mazo de políticas.

        Args:
            policies (list): Lista de políticas en el mazo.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        self.logger.info("\n===== POLICY DECK SHUFFLED =====\n")
        self.logger.info("Policies in deck: %s", policies)

    def log_month_change(self, game, level=LogLevel.NORMAL):
        """Registra el cambio de mes en el estado del juego.

        Args:
            game: El juego actual.
            level (LogLevel): Nivel de logging para este mensaje.
        """
        if level.value > self.level.value:
            return

        if hasattr(self, "logger"):
            self.logger.info("\n📅 %s begins...", game.state.get_current_month_name())
        if (
            game.state.month_counter == 10
            and not game.was_oktoberfest_active
            and game.state.oktoberfest_active
        ):
            self.logger.info(
                "\n🍺 OKTOBER FEST HAS BEGUN IN %s! All bots are now using random strategy for this month! 🍺",
                game.state.get_current_month_name().upper(),
            )
        elif (
            game.old_month == 10
            and game.state.month_counter == 11
            and not game.state.oktoberfest_active
        ):
            old_month_name = game.state.get_month_name(game.old_month)
            self.logger.info(
                "\n🍺 OKTOBER FEST HAS ENDED! %s is over and all bots have returned to their original strategies! 🍺",
                old_month_name,
            )
