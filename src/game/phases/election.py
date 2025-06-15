"""Election phase implementation for Secret Hitler XL game.

This module contains the ElectionPhase class which handles the nomination and voting
process for president and chancellor candidates in the game.
"""

from src.game.phases.abstract_phase import GamePhase


class ElectionPhase(GamePhase):
    """Handles the election phase of Secret Hitler XL.

    The election phase consists of:
    1. Checking for marked players to execute
    2. Nominating a chancellor candidate
    3. Voting on the government
    4. Handling election results and transitions

    Attributes:
        game: The main game instance containing state and methods.
    """

    def execute(self):
        """Execute the election phase logic.

        Performs the complete election cycle including:
        - Checking for pending executions
        - Chancellor nomination
        - Government voting
        - Win condition checks
        - Phase transitions

        Returns:
            GamePhase: The next phase to execute based on election results.
                - LegislativePhase: If government is elected successfully
                - GameOverPhase: If a win condition is met
                - ElectionPhase: If election fails and game continues

        Note:
            This method handles several critical game mechanics:
            - Chaos policy enactment after 3 failed elections
            - Hitler chancellor win condition
            - Term limit resets
            - Election tracker management
        """
        from src.game.phases.gameover import GameOverPhase
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

            # Government elected, go to legislative phase
            self.game.state.president = self.game.state.president_candidate
            self.game.state.chancellor = self.game.state.chancellor_candidate
            self.game.state.election_tracker = 0
            return LegislativePhase(self.game)
        else:
            self.game.state.president = self.game.state.president_candidate

            # Vote failed, advance the election tracker
            self.game.state.election_tracker += 1

            if self.game.state.election_tracker >= 3:
                self.game.logger.log(
                    "\n> Three failed elections in a row. Enacting a chaos policy."
                )
                # Enact top policy automatically
                self.game.enact_chaos_policy()
                self.game.state.election_tracker = 0

                # Check if the game is over
                if self.game.check_policy_win():
                    return GameOverPhase(self.game)

                # Reset term limits
                self.game.state.term_limited_players = []

            self.game.set_next_president()  # Stay in election phase for next round
            return self

    def _check_marked_for_execution(self):
        """Check and execute players marked for execution.

        Verifies if a player marked for execution should be killed based on
        the number of fascist policies enacted since they were marked.

        A player is executed if:
        - They are marked for execution
        - 3 or more fascist policies have been enacted since marking

        Returns:
            GameOverPhase: If Hitler is executed (liberal/communist win)
            None: If no execution occurs or non-Hitler player executed
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
