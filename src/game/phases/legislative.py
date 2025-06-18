"""Legislative phase implementation for Secret Hitler XL game.

This module contains the LegislativePhase class which handles policy drawing,
chancellor and president choices, veto power, policy enactment, and executive
actions in the game.
"""

from src.game.phases.abstract_phase import GamePhase
from src.game.phases.election import ElectionPhase
from src.game.phases.gameover import GameOverPhase


class LegislativePhase(GamePhase):
    """Handles the legislative phase of Secret Hitler XL.

    The legislative phase consists of:
    1. President draws 3 policies and discards 1
    2. Chancellor receives 2 policies and may propose veto
    3. President may accept/reject veto
    4. Chancellor enacts 1 policy and discards 1
    5. Executive power execution (if granted)
    6. Win condition checks
    7. Turn advancement and term limit updates

    Attributes:
        game: The main game instance containing state and methods.
    """

    def execute(self):
        """Execute the legislative phase logic.

        Performs the complete legislative cycle including:
        - Policy drawing and presidential choice
        - Veto proposal and resolution
        - Chancellor policy choice and enactment
        - Executive power execution
        - Win condition checks
        - Term limit management
        - Turn advancement

        Returns:
            GamePhase: The next phase to execute based on legislative results.
                - ElectionPhase: If veto succeeds or normal turn progression
                - GameOverPhase: If win condition is met or Hitler is executed
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
