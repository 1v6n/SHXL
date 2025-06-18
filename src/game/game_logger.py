import logging
from enum import Enum, auto


class LogLevel(Enum):

    NONE = auto()

    MINIMAL = auto()

    NORMAL = auto()

    VERBOSE = auto()

    DEBUG = auto()


class GameLogger:
    """Logger for game events"""

    def __init__(self, level=LogLevel.NORMAL):
        """


        Initialize the logger





        Args:


            level (LogLevel): Logging detail level


        """

        self.level = level

        # Set up logging

        logging.basicConfig(level=logging.INFO, format="%(message)s")

        self.logger = logging.getLogger("SHXL")

        # For tracking statistics

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
        """


        Log a message if the current log level is high enough





        Args:


            message (str): Message to log


            level (LogLevel): Level of this message


        """

        if level.value <= self.level.value:

            self.logger.info(message)

    def log_game_setup(self, game, level=LogLevel.NORMAL):
        """


        Log game setup information





        Args:


            game: The game object


        """

        if level.value > self.level.value:

            return

        self.logger.info("\n===== GAME SETUP =====\n")

        self.logger.info("Players: %d", game.player_count)

        # Only log role counts if roles have been assigned

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

        # Game options

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

        # Board configuration

        self.logger.info("Liberal track size: %d", game.state.board.liberal_track_size)

        self.logger.info("Fascist track size: %d", game.state.board.fascist_track_size)

        if game.communists_in_play:

            self.logger.info(
                "Communist track size: %d", game.state.board.communist_track_size
            )

        # Log the starting month
        self.logger.info(
            "\n🗓️ The game begins in %s!", game.state.get_current_month_name()
        )

        # Check if we're starting in Oktober Fest month
        if game.state.month_counter == 10:
            self.logger.info(
                "🍺 Starting in October - Oktober Fest is active from the beginning! All bots will use random strategy! 🍺"
            )

    def log_player_roles(self, players, level=LogLevel.DEBUG):
        """


        Log player roles (debug only - shows hidden information)





        Args:


            players: List of players


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
        """


        Log election results





        Args:


            president: President candidate


            chancellor: Chancellor candidate


            votes: List of votes


            result: Whether the vote passed


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

        # President info with role (if debug level)

        president_info = f"President candidate: {president.name}"

        if self.level.value == LogLevel.DEBUG.value:

            president_info += f" [{president.role.party_membership}"

            if president.is_hitler:

                president_info += "/Hitler"

            president_info += "]"

        self.logger.info(president_info)

        # Chancellor info with role (if debug level)

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

        # Detailed vote breakdown

        self.logger.info("Votes: %d Ja, %d Nein", ja_votes, nein_votes)

        self.logger.info("Individual votes:")

        if active_players:
            for player, vote in zip(active_players, votes):
                self.logger.info("  Player %d: %s", player.id, "Ja" if vote else "Nein")

        self.logger.info("Result: %s", "Passed" if result else "Failed")

    def log_drawn_policies(self, policies, level=LogLevel.DEBUG):
        """


        Log drawn policies (debug only - shows hidden information)





        Args:


            policies: List of drawn policies


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
        """


        Log politic policy selection (debug only - shows hidden information)





        Args:


            politic: President or Chancellor player


            chosen: Policies/policy that were chosen


            discarded: Policies/policy that were discarded


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
        """


        Log policy enactment





        Args:


            policy: Policy enacted


            track_position: Position on the track


            power: Power granted


        """

        if level.value > self.level.value:

            return

        # Update statistics

        self.policy_stats[policy.type] += 1

        self.logger.info("===== POLICY ENACTED =====")

        self.logger.info("Policy enacted: %s", policy.type)

        self.logger.info("Track position: %d", track_position)

        if power:

            self.logger.info("Power granted: %s", power)

        # Show current policy statistics

        if self.level.value >= LogLevel.NORMAL.value:

            self.logger.info("Current policy statistics:")

            for policy_type, count in self.policy_stats.items():

                if count > 0:  # Only show policies that have been enacted

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
        """


        Log presidential power usage





        Args:


            power: Power used


            president: President


            target: Target of the power


            result: Result of the power


        """

        if level.value > self.level.value:

            return

        self.logger.info("\n===== POWER USED =====\n")

        if is_president:

            politic_info = f"President: {politic.name}"

        else:

            politic_info = f"Chancellor: {politic.name}"

        # Add role info if debug level

        if self.level.value == LogLevel.DEBUG.value:

            politic_info += f" [{politic.role.party_membership}]"

        self.logger.info(politic_info)

        self.logger.info("Power: %s", power)

        if target:

            # Target info with role (if debug level)

            target_info = f"Target: {target.name}"

            if self.level.value == LogLevel.DEBUG.value:

                target_info += f" [{target.role.party_membership}"

                if target.is_hitler:

                    target_info += "/Hitler"

                target_info += "]"

            self.logger.info(target_info)

        # Show the result if provided

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
        """


        Log the usage of an anti-policy





        Args:


            policy_type: Type of anti-policy used


            player: The player who used it


        """

        if level.value > self.level.value:

            return

        self.logger.info("\n===== ANTI-POLICY USED =====\n")

        self.logger.info("Player %d (%s) used %s", player.id, player.name, policy_type)

    def log_emergency_power_usage(self, power_name, player):
        """


        Log the usage of an emergency power





        Args:


            power_name: Name of the emergency power


            player: The player who used it


        """

        if self.level.value < LogLevel.NORMAL.value:

            return

        self.logger.info("\n===== EMERGENCY POWER =====\n")

        self.logger.info("%s used %s", player.name, power_name)

        self.logger.info("\n===========================\n")

    def log_game_end(self, winner, players, game):
        """


        Log game end





        Args:


            winner: Winning team


        """

        # Log all player roles and affiliations

        self.logger.info("\n===== ROLE REVEALS =====\n")

        # Group players by affiliation

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

        # Log each group

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

        # Winner team info

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
        """


        Log current game state





        Args:


            game: The game instance


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

        # Show active players

        active_player_info = "Active players: "

        active_player_info += ", ".join(
            [f"Player {p.id}" for p in game.state.active_players]
        )

        self.logger.info(active_player_info)

        # Show dead players if any

        dead_players = [p for p in game.state.players if p.is_dead]

        if dead_players:

            dead_player_info = "Dead players: "

            dead_player_info += ", ".join([f"Player {p.id}" for p in dead_players])

            self.logger.info(dead_player_info)

        if level.value == LogLevel.DEBUG.value:

            self.logger.info("Policies in deck: %d", len(game.state.board.policies))

            self.logger.info("Policies in discard: %d", len(game.state.board.discards))

    def log_player_death(self, player, level=LogLevel.NORMAL):
        """


        Log player death





        Args:


            player: Player who died


        """

        if level.value > self.level.value:

            return

        self.logger.info("\n===== PLAYER DEATH =====\n")

        self.logger.info("Player %s has been executed", player.name)

    def log_chaos(self, policy, level=LogLevel.NORMAL):
        """


        Log chaos policy enactment





        Args:


            policy: Policy enacted due to chaos


        """

        if level.value > self.level.value:

            return

        self.logger.info("\n===== CHAOS =====\n")

        self.logger.info("Chaos policy enacted: %s", policy.type)

        self.logger.info("Presidential power not activated")

        self.logger.info("Term limits lifted for next election")

    def log_policy_deck(self, policies, level=LogLevel.DEBUG):
        """


        Log the policy deck





        Args:


            policies: List of policies in the deck


        """

        if level.value > self.level.value:

            return

        self.logger.info("\n===== POLICY DECK =====\n")

        self.logger.info("Policies in deck: %s", policies)

    def log_shuffle(self, policies, level=LogLevel.DEBUG):
        """


        Log the shuffle of the policy deck





        Args:


            policies: List of policies in the deck


        """

        if level.value > self.level.value:

            return

        self.logger.info("\n===== POLICY DECK SHUFFLED =====\n")

        self.logger.info("Policies in deck: %s", policies)

    def log_month_change(self, game, level=LogLevel.NORMAL):
        """
        Log the change of month in the game state
        Args:
            game_state: The current game state
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
