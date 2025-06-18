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
    """Main game class for Secret Hitler XL"""

    def __init__(self, logger=None):
        """

        Initialize a new game



        Args:

            player_factory: Factory to create players

            logger: Game logger (optional)

        """

        self.logger = logger if logger else GameLogger(LogLevel.NORMAL)

        self.current_phase = None

        self.state = EnhancedGameState()

        self.communists_in_play = False

        self.anti_policies_in_play = False

        self.emergency_powers_in_play = False

        self.human_player_indices = []  # Initialize human player indices

        self.ai_strategy = "role"  # Default to smart strategy for AI players

        self.player_count = 0  # Initialize player_count attribute

        self.hitler_player = None  # Initialize hitler_player attribute

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
        """

        Set up the game with the given parameters



        Args:

            player_count: Number of players

            with_communists: Whether to include communists

            with_anti_policies: Whether to include anti-policies

            with_emergency_powers: Whether to include emergency powers

            human_player_indices: List of player indices that should be human-controlled

            ai_strategy: Strategy to use for AI players

        """

        # Only allow anti-policies when communists are enabled

        if with_anti_policies and not with_communists:

            with_anti_policies = False

        self.player_count = player_count

        self.communists_in_play = with_communists

        self.anti_policies_in_play = with_anti_policies

        self.emergency_powers_in_play = with_emergency_powers

        self.human_player_indices = human_player_indices or []

        self.ai_strategy = ai_strategy

        self.state = EnhancedGameState()

        # Add tracking structures for government history and policy enactments

        self.state.government_history = []

        self.state.policy_history = []

        # Set up the board

        self.initialize_board(self.player_count, self.communists_in_play)

        # Create the policy deck

        policy_factory = PolicyFactory()

        self.state.board.initialize_policy_deck(
            policy_factory, with_anti_policies, with_emergency_powers
        )

        self.assign_players()

        self.inform_players()

        self.choose_first_president()

        self.logger.log_game_setup(self)

        from src.game.phases.setup import SetupPhase

        # Check if we're starting in Oktober Fest month
        if self.state.month_counter == 10:
            # Manually trigger Oktober Fest since we're starting in October
            self.state._start_oktoberfest()

        # Enter the election phase

        self.current_phase = SetupPhase(self)
        self.state.set_phase("setup")

    def initialize_board(self, players, communist_flag):
        """Initialize the game board"""

        self.state.board = GameBoard(self.state, players, communist_flag)

    def start_game(self):
        """

        Run the game from beginning to end



        Returns:

            str: The winner of the game

        """

        # Run phases until game is over
        if self.state.current_phase_name == "setup":
            from src.game.phases.election import ElectionPhase

            self.current_phase = ElectionPhase(self)
            self.state.set_phase("election")
        while not self.state.game_over:

            next_phase = self.current_phase.execute()
            self.current_phase = next_phase

            # 🔧 SIMPLE: Solo actualizar string
            if isinstance(next_phase, type(self.current_phase)):
                # Misma fase, no cambiar
                pass
            else:
                # Nueva fase, actualizar
                new_phase_name = next_phase.__class__.__name__.lower().replace(
                    "phase", ""
                )
                self.state.set_phase(new_phase_name)
        # End of game
        self.state.transition_to_phase("game_over")  # End of game

        self.logger.log_game_end(self.state.winner, self.state.players, self)

        # Return the winner

        return self.state.winner

    def get_current_phase_info(self):
        """SIMPLE - Obtener info de fase actual"""
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
        """

        Create players and assign roles

        Uses the player factory to create players

        Uses the role factory to create roles

        """

        # Create players

        player_factory = PlayerFactory()

        player_factory.create_players(
            self.player_count,
            self.state,
            strategy_type=self.ai_strategy,
            human_player_indices=self.human_player_indices or [],
        )

        # Initialize the active_players list with all players

        self.state.active_players = self.state.players.copy()

        # Generate roles for players

        role_factory = RoleFactory()

        roles = role_factory.create_roles(
            self.player_count, with_communists=self.communists_in_play
        )

        # Assign roles to players

        for i, player in enumerate(self.state.players):

            player.role = roles[i]

            player.initialize_role_attributes()

        # Get the Hitler player

        self.hitler_player = next(p for p in self.state.players if p.is_hitler)

        # Now that roles have been assigned, update player strategies based on strategy_type

        player_factory.update_player_strategies(self.state.players, self.ai_strategy)

    def inform_players(self):
        """Inform players of their roles and other players they should know about"""

        # Handle fascist knowledge

        self._inform_fascists()

        # Handle communist knowledge

        if self.communists_in_play:

            self._inform_communists()

    def _inform_fascists(self):
        """Inform fascists about each other and Hitler"""

        fascists = [p for p in self.state.players if p.is_fascist and not p.is_hitler]

        # Inform each fascist about Hitler and other fascists

        for fascist in fascists:

            # Always know Hitler

            fascist.hitler = self.hitler_player

            # Always know other fascists

            # In games with < 8 players, Hitler knows the fascists

            fascist.fascists = fascists

        if self.player_count < 8:

            self.hitler_player.fascists = fascists

    def _inform_communists(self):
        """Inform communists about each other if applicable"""

        communists = [p for p in self.state.players if p.is_communist]

        # In games with < 11 players, communists know each other

        if self.player_count < 11:

            for communist in communists:

                communist.known_communists = [
                    c.id for c in communists if c != communist
                ]

    def choose_first_president(self):
        """Choose the first president randomly"""

        # Random player becomes president candidate

        random_index = randint(0, len(self.state.active_players) - 1)

        chosen_president = self.state.active_players[random_index]

        # Set BOTH president and president_candidate to the same player
        self.state.president = chosen_president
        self.state.president_candidate = chosen_president

        # Ensure no chancellor is set initially
        self.state.chancellor = None
        self.state.chancellor_candidate = None

        # Initialize government tracking if not present
        if not hasattr(self.state, "government_history"):
            self.state.government_history = []
        if not hasattr(self.state, "previous_government"):
            self.state.previous_government = None

    def set_next_president(self):
        """Set the next president based on rotation"""

        # Check if Oktober Fest was just starting before advancing
        self.was_oktoberfest_active = self.state.oktoberfest_active
        self.old_month = self.state.month_counter

        self.state.set_next_president()

        self.logger.log_month_change(self)

    def advance_turn(self):
        """

        Advance the game to the next turn.

        Increments the round number and sets the next president.

        Used primarily for testing the game flow.

        """

        self.state.round_number += 1

        self.set_next_president()
        if hasattr(self.state, "president") and self.state.president:
            self.state.president_candidate = self.state.president
        return self.state.president_candidate

    def nominate_chancellor(self):
        """

        Ask the president to nominate a chancellor



        Returns:

            player: The nominated chancellor

        """

        eligible_chancellors = self.state.get_eligible_chancellors()

        if not eligible_chancellors:

            return None

        return self.state.president_candidate.nominate_chancellor(eligible_chancellors)

    def vote_on_government(self):
        """

        Have all players vote on the proposed government



        Returns:

            bool: True if the vote passed, False otherwise

        """

        self.state.last_votes = []

        # Get votes from all living players

        for player in self.state.active_players:

            vote = player.vote()

            self.state.last_votes.append(vote)

        # Count votes

        ja_votes = sum(1 for vote in self.state.last_votes if vote)

        nein_votes = len(self.state.last_votes) - ja_votes

        # Vote passes if majority is in favor

        vote_passed = ja_votes > nein_votes

        if vote_passed:

            # Reset election tracker

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

            # Track this government for future reference

            if not hasattr(self.state, "government_history"):

                self.state.government_history = []

            # Add this government to history

            self.state.government_history.append(
                {
                    "president": self.state.president_candidate,
                    "chancellor": self.state.chancellor_candidate,
                    "round": self.state.round_number,
                    "votes": self.state.last_votes,
                }
            )
        else:
            # Election failed - advance election tracker
            self.state.election_tracker += 1

        # Log the election with enhanced information

        self.logger.log_election(
            self.state.president_candidate,
            self.state.chancellor_candidate,
            self.state.last_votes,
            vote_passed,
            self.state.active_players,
        )

        return vote_passed

    def enact_chaos_policy(self):
        """

        Enact the top policy automatically due to failed governments



        Returns:

            str: The enacted policy type

        """

        # Draw and enact top policy

        top_policy = self.state.board.draw_policy(1)[0]

        self.logger.log_chaos(top_policy)

        # Reset election tracker

        self.state.board.enact_policy(top_policy, chaos=True)

        self.state.election_tracker = 0

        self.state.enacted_policies += 1

        return top_policy.type

    def check_policy_win(self):
        """

        Check if a policy win condition has been met



        Returns:

            bool: True if a policy win condition is met

        """

        self.logger.log(
            f"\nPolicy trackers - Liberal: {self.state.board.liberal_track}/{self.state.board.liberal_track_size}, Fascist: {self.state.board.fascist_track}/{self.state.board.fascist_track_size}, Communist: {self.state.board.communist_track}/{self.state.board.communist_track_size}"
        )

        # Check liberal win

        if self.state.board.liberal_track >= self.state.board.liberal_track_size:

            self.state.game_over = True

            self.state.winner = "liberal"

            return True

        # Check fascist win

        if self.state.board.fascist_track >= self.state.board.fascist_track_size:

            self.state.game_over = True

            self.state.winner = "fascist"

            return True

        # Check communist win

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
        """

        Ask the president to choose policies



        Args:

            policies: List of 3 policies



        Returns:

            tuple: (chosen [2], discarded [1])

        """

        chosen, discarded = self.state.president.filter_policies(policies)

        self.state.last_discarded = discarded

        self.logger.log_policy_selection(
            self.state.president, chosen, discarded, is_chancellor=False
        )

        return chosen, discarded

    def chancellor_propose_veto(self):
        """

        Ask the chancellor if they want to veto



        Args:

            policies: List of 2 policies



        Returns:

            bool: True if veto proposed, False otherwise

        """

        if not self.state.board.veto_available:

            return False

        return self.state.chancellor.veto()

    def president_veto_accepted(self):
        """

        Ask the president if they accept the veto



        Returns:

            bool: True if veto accepted, False otherwise

        """

        return self.state.president.accept_veto()

    def chancellor_policy_choice(self, policies):
        """

        Ask the chancellor to choose a policy



        Args:

            policies: List of 2 policies



        Returns:

            chosen, discarded

        """

        chosen, discarded = self.state.chancellor.choose_policy(policies)

        self.state.last_discarded = discarded

        self.logger.log_policy_selection(self.state.chancellor, chosen, discarded)

        return chosen, discarded

    def get_fascist_power(self):
        """

        Get the fascist power for the current track position



        Returns:

            str or None: The power to use

        """

        # Check if power should be blocked

        if self.state.block_next_fascist_power:

            self.state.block_next_fascist_power = False

            return None

        return self.state.board.get_power_for_track_position(
            "fascist", self.state.board.fascist_track
        )

    def get_communist_power(self):
        """

        Get the communist power for the current track position



        Returns:

            str or None: The power to use

        """

        # Check if power should be blocked

        if self.state.block_next_communist_power:

            self.state.block_next_communist_power = False

            return None

        return self.state.board.get_power_for_track_position(
            "communist", self.state.board.communist_track
        )

    def execute_power(self, power_name):
        """

        Execute a power



        Args:

            power_name: Name of the power



        Returns:

            Any: Result of the power

        """

        # Determine the owner of the power

        power_owner = PowerRegistry.get_owner(power_name)

        # Execute the power based on its owner

        if power_owner == PowerOwner.PRESIDENT:

            return self.execute_presidential_power(power_name)

        elif power_owner == PowerOwner.CHANCELLOR:

            return self.execute_chancellor_power(power_name)

        else:

            raise ValueError(f"Unknown power owner for power: {power_name}")

    def execute_presidential_power(self, power_name):
        """

        Execute a power owned by the president



        Args:

            power_name: Name of the power



        Returns:

            Any: Result of the power

        """

        # Get the power

        power = PowerRegistry.get_power(power_name, self)

        # For advanced logging

        power_result = None

        power_target = None

        # Execute based on type

        if power_name in ["chancellor_propaganda", "chancellor_policy_peek"]:
            power_result = power.execute()
            return power_result

        if power_name in ["propaganda", "policy_peek_emergency"]:

            # View cards

            power_result = power.execute()

        elif power_name == "investigate_loyalty":

            # President investigates a player's party membership

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]

            target = self.state.president.choose_player_to_investigate(eligible_players)

            power_target = target

            power_result = power.execute(target)

        elif power_name == "special_election":

            # President chooses the next president

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]

            next_president = self.state.president.choose_next_president(
                eligible_players
            )

            power_target = next_president

            power_result = power.execute(next_president)

        elif power_name == "policy_peek":

            # President views the top 3 policies

            power_result = power.execute()

        elif power_name == "execution":

            # President executes a player

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]

            target = self.state.president.kill()

            power_target = target

            power_result = power.execute(target)

            self.logger.log_player_death(target)

        elif power_name == "confession":

            # President reveals their own party membership

            power_result = power.execute()

        elif power_name == "bugging":

            # Communists view another player's party membership

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]

            target = self.state.president.choose_player_to_bug(eligible_players)

            power_target = target

            power_result = power.execute(target)

        elif power_name == "five_year_plan":

            # Add 2 communist and 1 liberal policy to the deck

            power_result = power.execute()

        elif power_name == "congress":

            # Communists learn who the original communists are

            power_result = power.execute()

        elif power_name == "radicalization":

            # Convert a player to communist

            target = self.state.president.choose_player_to_radicalize()

            power_target = target

            power_result = power.execute(target)

        elif power_name == "impeachment":

            # President chooses who sees the chancellor's party

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

            # President marks a player for execution

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]

            target = self.state.president.choose_player_to_mark()

            power_target = target

            power_result = power.execute(target)

        elif power_name == "execution_emergency":

            # President executes a player directly

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.president.id
            ]

            target = self.state.president.kill()

            power_target = target

            power_result = power.execute(target)

            self.logger.log_player_death(target)

        elif power_name == "pardon":

            # President may pardon a marked player

            should_pardon = self.state.president.pardon_player()

            if should_pardon:

                power_result = power.execute()

                power_target = power_result

            else:

                self.logger.log(
                    f"President {self.state.president.id} ({self.state.president.name}) chose not to pardon."
                )

        # Additional detailed logging if needed

        if power_target or power_result:

            self.logger.log_power_used(
                power_name, self.state.president, power_target, power_result
            )

        return power_result

    def execute_chancellor_power(self, power_name):
        """

        Execute a power owned by the chancellor



        Args:

            power_name: Name of the power



        Returns:

            Any: Result of the power

        """

        # Get the power

        power = PowerRegistry.get_power(power_name, self)

        power_result = None

        power_target = None

        # Execute based on type

        if power_name in ["chancellor_propaganda", "chancellor_policy_peek"]:

            # View cards

            power_result = power.execute()

        elif power_name == "chancellor_impeachment":

            # Chancellor reveals their party to a player chosen by the president

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

            # Chancellor marks a player for execution

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.chancellor.id
            ]

            target = self.state.chancellor.choose_player_to_mark()

            power_target = target

            power_result = power.execute(target)

        elif power_name == "chancellor_execution":

            # Chancellor executes a player directly

            eligible_players = [
                p for p in self.state.active_players if p.id != self.state.chancellor.id
            ]

            target = self.state.chancellor.kill()

            power_target = target

            power_result = power.execute(target)

            self.logger.log_player_death(target)

        elif power_name == "vote_of_no_confidence":

            # Special chancellor power to enact discarded policy

            power_result = power.execute()

        # Additional detailed logging if needed

        if power_target and power_result:
            self.logger.log_power_used(
                power_name, self.state.chancellor, power_target, power_result
            )

        return power_result
