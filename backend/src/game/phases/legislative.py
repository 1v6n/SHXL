"""Implementación de la fase legislativa para el juego Secret Hitler XL.

Este módulo contiene la clase LegislativePhase que maneja el sorteo de políticas,
las decisiones del canciller y presidente, el poder de veto, la promulgación de políticas
y las acciones ejecutivas en el juego.
"""

from src.game.phases.abstract_phase import GamePhase
from src.game.phases.election import ElectionPhase
from src.game.phases.gameover import GameOverPhase


class LegislativePhase(GamePhase):
    """Maneja la fase legislativa de Secret Hitler XL.

    La fase legislativa consiste en:
    1. El Presidente roba 3 políticas y descarta 1
    2. El Canciller recibe 2 políticas y puede proponer veto
    3. El Presidente puede aceptar/rechazar el veto
    4. El Canciller promulga 1 política y descarta 1
    5. Ejecución de poder ejecutivo (si se otorga)
    6. Verificación de condiciones de victoria
    7. Avance de turno y actualización de límites de mandato

    Attributes:
        game: La instancia principal del juego que contiene el estado y métodos.
    """

    def execute(self):
        """Ejecuta la lógica de la fase legislativa.

        Realiza el ciclo legislativo completo incluyendo:
        - Sorteo de políticas y elección presidencial
        - Propuesta y resolución de veto
        - Elección y promulgación de política del canciller
        - Ejecución de poder ejecutivo        - Verificación de condiciones de victoria
        - Gestión de límites de mandato
        - Avance de turno

        Returns:
            GamePhase: La siguiente fase a ejecutar basada en los resultados legislativos.
                - ElectionPhase: Si el veto tiene éxito o progresión normal de turno
                - GameOverPhase: Si se cumple una condición de victoria o Hitler es ejecutado
        """

        policies = self.game.state.board.draw_policy(3)

        chosen, discarded = self.game.presidential_policy_choice(policies)
        self.game.state.board.discard(discarded)

        chancellor_vetoed = self.game.chancellor_propose_veto()

        if chancellor_vetoed:
            president_accepted = self.game.president_veto_accepted()
            if president_accepted:
                self.game.state.board.discard(chosen)
                self.game.state.election_tracker += 1
                return ElectionPhase(self.game)

        enacted, discarded = self.game.chancellor_policy_choice(chosen)
        self.game.state.board.discard(discarded)

        power_granted = self.game.state.board.enact_policy(
            enacted,
            False,
            self.game.emergency_powers_in_play,
            self.game.anti_policies_in_play,
        )

        self.game.state.election_tracker = 0

        self.game.state.term_limited_players = []

        last_president_served = self.game.state.president
        last_chancellor_served = self.game.state.chancellor

        if len(self.game.state.active_players) > 7:
            if last_president_served:
                self.game.state.term_limited_players.append(last_president_served)
            if (
                last_chancellor_served
                and last_chancellor_served != last_president_served
            ):
                self.game.state.term_limited_players.append(last_chancellor_served)
        else:
            if last_chancellor_served:
                self.game.state.term_limited_players.append(last_chancellor_served)

        if self.game.check_policy_win():
            return GameOverPhase(self.game)

        if power_granted:
            result = self.game.execute_power(power_granted)

            if power_granted == "execution" and result and result.is_hitler:
                self.game.state.game_over = True
                if self.game.communists_in_play:
                    self.game.state.winner = "liberal_and_communist"
                    self.game.logger.log(
                        "Hitler was executed! Liberals and Communists win!"
                    )
                else:
                    self.game.state.winner = "liberal"
                    self.game.logger.log("Hitler was executed! Liberals win!")
                return GameOverPhase(self.game)

        self.game.advance_turn()
        return ElectionPhase(self.game)
