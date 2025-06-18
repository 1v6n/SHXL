from random import randint


class EnhancedGameState:
    """Enhanced game state to support all SHXL features"""

    def __init__(self):
        # Game status
        self.game_over = False
        self.winner = None
        self.round_number = 0
        self.current_phase_name = "setup"  # Fase actual como string simple

        # Players
        self.players = []  # All players
        self.active_players = []  # Non-dead players

        # Election-phase related
        self.president = None  # Current president
        self.president_candidate = None  # Current candidate
        self.chancellor = None  # Current chancellor
        self.chancellor_candidate = None  # Current candidate
        self.election_tracker = 0  # Number of failed elections
        self.last_votes = []  # Votes from last election
        self.term_limited_players = (
            []
        )  # Players who can't be chancellor in the current round (last elected government)

        # Special election
        self.special_election = False
        self.special_election_return_index = None

        # Legislative state
        self.veto_available = False  # Available after 5 fascist policies
        self.last_discarded = None  # Last discarded policy

        # Policy trackers
        self.liberal_track = 0
        self.fascist_track = 0
        self.communist_track = 0

        # Powers
        self.investigated_players = []  # Players who have been investigated
        self.known_communists = {}  # Dict of player ID -> whether they're communist
        self.revealed_affiliations = {}  # Dict of player ID -> revealed party
        self.marked_for_execution = []  # Players marked for execution
        self.enacted_policies = 0
        # Fascist track position when player was marked
        self.marked_for_execution_tracker = None

        # Power blocking
        self.block_next_fascist_power = False
        self.block_next_communist_power = False

        # Board
        self.board = None

        # Most recent policy
        self.most_recent_policy = (
            None  # Current policies being considered by chancellor/president
        )
        self.current_policies = []  # Month counter and Oktober Fest tracking
        self.month_counter = randint(1, 12)  # Starts at month 1
        self.oktoberfest_active = False  # Whether Oktober Fest is currently active
        self.original_strategies = {}  # Store original strategies during Oktober Fest

        # Month names mapping
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
        """Get the current month name"""
        return self.month_names.get(self.month_counter, f"Month {self.month_counter}")


    def set_phase(self, phase_name):
        """Cambiar la fase actual - SIMPLE"""
        self.current_phase_name = phase_name

    def get_month_name(self, month_number):
        """Get the name of a specific month"""
        return self.month_names.get(month_number, f"Month {month_number}")

    def reset_election_tracker(self):
        """Reset the election tracker to 0"""
        self.election_tracker = 0

    def add_player(self, player):
        """
        Add a player to the game

        Args:
            player: Player to add
        """
        self.players.append(player)
        self.active_players.append(player)

    def get_eligible_chancellors(self):
        """
        Get players eligible to be chancellor

        Returns:
            list: Eligible players
        """
        eligible = []

        for player in self.active_players:

            # Skip the president
            if player == self.president_candidate:
                continue

            # Skip term-limited players
            if player in self.term_limited_players:
                continue  # Skip dead players
            if player.is_dead:
                continue

            eligible.append(player)

        return eligible

    def get_next_president_index(self):
        """
        Get the index of the next president

        Returns:
            int: Index of the next president
        """
        # After a special election, return to the original rotation
        if self.special_election:
            self.special_election = False
            return (self.special_election_return_index + 1) % len(self.active_players)

        # Normal rotation - find current president in active players and get next
        if self.president is None:
            return 0

        current_index = self.active_players.index(self.president)
        return (current_index + 1) % len(self.active_players)

    def handle_player_death(self, player):
        """
        Handle a player's death

        Args:
            player: The player who died
        """
        player.is_dead = True

        # If the president is dying, we need to handle presidency first
        was_president = player == self.president
        if was_president:
            # Find current president index before removing from active players
            current_president_index = self.active_players.index(self.president)

        # Remove from active players
        if player in self.active_players:
            self.active_players.remove(player)

        # Set next president if the current president died
        if was_president:
            # Calculate next president index based on old position
            next_index = (current_president_index) % len(self.active_players)
            self.president_candidate = self.active_players[next_index]
            self.president = None  # Clear current president

    def advance_month_counter(self):
        """Advance the month counter and handle Oktober Fest logic"""
        # Increment month counter first
        self.month_counter += 1

        # Reset to 1 after month 12
        if self.month_counter > 12:
            self.month_counter = 1  # Handle Oktober Fest logic
        if self.month_counter == 10:
            # Start Oktober Fest when entering October (month 10)
            self._start_oktoberfest()
        elif self.month_counter == 11 and self.oktoberfest_active:
            # End Oktober Fest when leaving October and entering November (month 11)
            self._end_oktoberfest()

    def _start_oktoberfest(self):
        """Start Oktober Fest - save original strategies and switch bots to random"""
        if self.oktoberfest_active:
            return  # Already active

        self.oktoberfest_active = True
        self.original_strategies = {}

        # Import RandomStrategy here to avoid circular imports
        from src.players.strategies.random_strategy import RandomStrategy

        # Save original strategies and switch all bots to random strategy
        for player in self.active_players:
            if hasattr(player, "is_bot") and player.is_bot:
                # Save original strategy
                self.original_strategies[player.id] = player.strategy
                # Switch to random strategy
                player.strategy = RandomStrategy(player)

    def _end_oktoberfest(self):
        """End Oktober Fest - restore original strategies"""
        if not self.oktoberfest_active:
            return  # Not active

        self.oktoberfest_active = False
        # Restore original strategies
        for player in self.active_players:
            if (
                hasattr(player, "is_bot")
                and player.is_bot
                and player.id in self.original_strategies
            ):
                player.strategy = self.original_strategies[player.id]

        # Clear saved strategies
        self.original_strategies = {}

    def set_next_president(self):
        """Set the next president based on rotation and advance month counter"""
        next_index = self.get_next_president_index()
        self.president_candidate = self.active_players[next_index]

        # Advance the month counter each time we set a new president (each election)
        self.advance_month_counter()
