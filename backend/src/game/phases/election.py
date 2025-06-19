"""Implementación de la fase electoral para el juego Secret Hitler XL.

Este módulo contiene la clase ElectionPhase que maneja el proceso de nominación y
votación para candidatos a presidente y canciller en el juego.
"""

from src.game.phases.abstract_phase import GamePhase
from src.game.phases.gameover import GameOverPhase


class ElectionPhase(GamePhase):
    """Maneja la fase electoral de Secret Hitler XL.

    La fase electoral consiste en:
    1. Verificación de jugadores marcados para ejecución
    2. Nominación de candidato a canciller
    3. Votación sobre el gobierno propuesto
    4. Manejo de resultados electorales y transiciones

    Attributes:
        game: La instancia principal del juego que contiene el estado y métodos.
    """

    def execute(self):
        """Ejecuta la lógica de la fase electoral.

        Realiza el ciclo electoral completo incluyendo:
        - Verificación de ejecuciones pendientes
        - Nominación del canciller
        - Votación del gobierno
        - Verificación de condiciones de victoria
        - Transiciones de fase

        Returns:
            GamePhase: La siguiente fase a ejecutar basada en los resultados electorales.
                - LegislativePhase: Si el gobierno es elegido exitosamente
                - GameOverPhase: Si se cumple una condición de victoria
                - ElectionPhase: Si la elección falla y el juego continúa        Note:
            Este método maneja varias mecánicas críticas del juego:
            - Promulgación de política de caos después de 3 elecciones fallidas
            - Condición de victoria de Hitler como canciller
            - Restablecimiento de límites de mandato
            - Gestión del contador electoral
        """

        from src.game.phases.legislative import LegislativePhase

        self._check_marked_for_execution()

        self.game.state.chancellor_candidate = self.game.nominate_chancellor()

        if self.game.state.chancellor_candidate is None:
            self.game.logger.log(
                "\n> No eligible chancellor candidates. Enacting a chaos policy."
            )
            self.game.enact_chaos_policy()
            self.game.state.election_tracker = 0

            if self.game.check_policy_win():
                return GameOverPhase(self.game)

            self.game.state.term_limited_players = []
            return self

        vote_passed = self.game.vote_on_government()

        if vote_passed:
            if (
                self.game.state.fascist_track >= 3
                and self.game.state.chancellor_candidate.is_hitler
            ):
                self.game.state.winner = "fascist"
                return GameOverPhase(self.game)

            self.game.state.president = self.game.state.president_candidate
            self.game.state.chancellor = self.game.state.chancellor_candidate
            self.game.state.election_tracker = 0
            return LegislativePhase(self.game)
        else:
            self.game.state.president = self.game.state.president_candidate

            self.game.state.election_tracker += 1

            if self.game.state.election_tracker >= 3:
                self.game.logger.log(
                    "\n> Three failed elections in a row. Enacting a chaos policy."
                )
                self.game.enact_chaos_policy()
                self.game.state.election_tracker = 0

                if self.game.check_policy_win():
                    return GameOverPhase(self.game)

                self.game.state.term_limited_players = []

            self.game.set_next_president()
            return self

    def _check_marked_for_execution(self):
        """Verifica y ejecuta jugadores marcados para ejecución.

        Verifica si un jugador marcado para ejecución debe ser eliminado basándose en
        el número de políticas fascistas promulgadas desde que fue marcado.

        Un jugador es ejecutado si:
        - Está marcado para ejecución
        - Se han promulgado 3 o más políticas fascistas desde el marcado

        Returns:
            GameOverPhase: Si Hitler es ejecutado (victoria liberal/comunista)
            None: Si no ocurre ejecución o se ejecuta un jugador no-Hitler
        """
        if (
            hasattr(self.game.state, "marked_for_execution")
            and self.game.state.marked_for_execution is not None
            and hasattr(self.game.state, "marked_for_execution_tracker")
            and self.game.state.marked_for_execution_tracker is not None
        ):
            fascist_policies_enacted = (
                self.game.state.board.fascist_track
                - self.game.state.marked_for_execution_tracker
            )

            self.game.logger.log(
                f"Checking marked for execution: Player {self.game.state.marked_for_execution.id}, "
                f"Fascist track now: {self.game.state.board.fascist_track}, "
                f"Fascist track at marking: {self.game.state.marked_for_execution_tracker}, "
                f"Policies enacted since marking: {fascist_policies_enacted}"
            )

            if fascist_policies_enacted >= 3:
                player = self.game.state.marked_for_execution

                self.game.logger.log(
                    f"EXECUTING: Player {player.id} ({player.name}) is being executed. "
                    f"Marked when fascist track was {self.game.state.marked_for_execution_tracker}. "
                    f"Current fascist track is {self.game.state.board.fascist_track}."
                )

                player.is_dead = True
                if player in self.game.state.active_players:
                    self.game.state.active_players.remove(player)

                self.game.state.marked_for_execution = None
                self.game.state.marked_for_execution_tracker = None

                if player.is_hitler:
                    if self.game.communists_in_play:
                        self.game.state.winner = "liberal_and_communist"
                        self.game.logger.log(
                            "Hitler was executed! Liberals and Communists win!"
                        )
                    else:
                        self.game.state.winner = "liberal"
                        self.game.logger.log("Hitler was executed! Liberals win!")
                    return GameOverPhase(self.game)
            else:
                self.game.logger.log(
                    f"Player {self.game.state.marked_for_execution.id} has "
                    f"{3 - fascist_policies_enacted} more fascist policies needed for execution."
                )
