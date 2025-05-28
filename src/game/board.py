from random import shuffle

# !This can be used to balance the game
VETO_POWER_THRESHOLD = 5


class GameBoard(object):
    """Represents the game board with policy trackers and powers"""

    def __init__(self, game_state, player_count, with_communists=True):
        """
        Initialize the game board

        Args:
            game_state: The game state
            player_count: Number of players
            with_communists: Whether communists are in play
        """
        self.state = game_state
        self.player_count = player_count
        self.with_communists = with_communists

        # Initialize policy trackers
        self.liberal_track_size = 5  # Default size
        self.fascist_track_size = 6  # Always 6
        self.communist_track_size = self._get_communist_track_size()

        # Initialize policy counts
        self.liberal_track = 0
        self.fascist_track = 0
        self.communist_track = 0
        self.policies = []
        self.discards = []

        # Set up power slots based on player count
        self.fascist_powers = self._setup_fascist_powers()
        self.communist_powers = self._setup_communist_powers()

        # Store Veto flag, which becomes available after 5 fascist policies
        self.veto_available = False

    def _get_communist_track_size(self):
        """Determine communist tracker size based on player count"""
        if not self.with_communists:
            return 0

        if self.player_count < 9:
            return 5
        else:
            return 6

    def _setup_fascist_powers(self):
        """Set up fascist power slots based on player count"""
        if self.player_count < 8:
            return [None, None, "policy_peek", "execution", "execution"]
        elif self.player_count < 11:
            return [
                None,
                "investigate_loyalty",
                "special_election",
                "execution",
                "execution",
            ]
        else:
            return [
                "investigate_loyalty",
                "investigate_loyalty",
                "special_election",
                "execution",
                "execution",
            ]

    def _setup_communist_powers(self):
        """Set up communist power slots based on player count"""
        if not self.with_communists:
            return []

        if self.player_count < 9:
            return ["bugging", "radicalization", "five_year_plan", "congress"]
        elif self.player_count < 11:
            return [
                "bugging",
                "radicalization",
                "five_year_plan",
                "congress",
                "confession",
            ]
        else:
            return [
                None,
                "radicalization",
                "five_year_plan",
                "radicalization",
                "confession",
            ]

    def initialize_policy_deck(
        self, policy_factory, with_anti_policies=False, with_emergency=False
    ):
        """
        Initialize the policy deck with the appropriate cards

        Args:
            policy_factory: Factory to create policies
            with_anti_policies: Whether to include anti-policies
            with_emergency: Whether to include emergency powers
        """
        self.policies = policy_factory.create_policy_deck(
            self.player_count, self.with_communists, with_anti_policies, with_emergency
        )
        self.discards = []

    def draw_policy(self, count=1):
        """
        Draw policies from the deck

        Args:
            count: Number of policies to draw

        Returns:
            list: List of drawn policies
        """

        # If there are not enough policies to be drawn, shuffle the remaining policies with the discard pile
        if len(self.policies) < count:
            # Add the discard pile into the draw pile
            self.policies.extend(self.discards)
            self.discards = []
            shuffle(self.policies)

        # Draw policies one by one to ensure they're unique objects
        drawn = []
        for _ in range(count):
            drawn.append(self.policies.pop(0))

        # Chaos policies
        if count > 1:
            print("Drawing chaos policy")

        return drawn

    def discard(self, policies):
        """
        Discard policies

        Args:
            policies: A policy or list of policies to discard
        """
        if not isinstance(policies, list):
            policies = [policies]

        self.discards.extend(policies)

    def enact_policy(self, policy, chaos=False, emergency=False, antipolicies=False):
        """
        Enact a policy on the appropriate track

        Args:
            policy: The policy to enact

        Returns:
            (str or None): Presidential power granted by this policy, if any
        """
        policy_type = policy.type
        power = None
        if policy_type == "liberal":
            self.liberal_track += 1
            if self.liberal_track >= self.liberal_track_size:
                self.state.game_over = True
                self.state.winner = "liberal"

        elif policy_type == "fascist":
            self.fascist_track += 1

            # Sync the game state's fascist track with the board's
            self.state.fascist_track = self.fascist_track

            # Check for power
            power = self.get_fascist_power() if not chaos else None

            # Check for win
            if self.fascist_track >= self.fascist_track_size:
                self.state.game_over = True
                self.state.winner = "fascist"

            # Check for veto power
            if self.fascist_track >= VETO_POWER_THRESHOLD:
                self.veto_available = True

        elif policy_type == "communist":
            self.communist_track += 1

            # Sync the game state's fascist track with the board's
            self.state.communist_track = self.communist_track

            # Check for power
            power = self.get_communist_power() if not chaos else None
            # Check for win
            if (
                self.communist_track >= self.communist_track_size
                and self.communist_track_size > 0
            ):
                self.state.game_over = True
                self.state.winner = "communist"

        if antipolicies is True:
            if policy_type == "antifascist":
                # Goes on communist track, removes a fascist policy
                self.communist_track += 1
                if self.fascist_track > 0:
                    self.fascist_track -= 1

                    # Sync the game state's fascist track with the board's
                    self.state.fascist_track = self.fascist_track

                    if self.fascist_track < VETO_POWER_THRESHOLD:
                        self.veto_available = False

                # Block next fascist power
                self.state.block_next_fascist_power = True

            elif policy_type == "anticommunist":
                # Goes on fascist track, removes a communist policy
                self.fascist_track += 1

                # Sync the game state's fascist track with the board's
                self.state.fascist_track = self.fascist_track

                if self.communist_track > 0:
                    self.communist_track -= 1

                # Block next communist power
                self.state.block_next_communist_power = True

            elif policy_type == "socialdemocratic":
                # Goes on liberal track, removes fascist or communist policy
                self.liberal_track += 1
                # Chancellor chooses which policy to remove
                remove = self.state.chancellor.social_democratic_removal_choice(
                    self.state
                )
                if remove == "fascist":
                    if self.fascist_track > 0:
                        self.fascist_track -= 1

                    # Sync the game state's fascist track with the board's
                    self.state.fascist_track = self.fascist_track

                    if self.fascist_track < VETO_POWER_THRESHOLD:
                        self.veto_available = False

                    self.state.block_next_fascist_power = True
                else:
                    if self.communist_track > 0:
                        self.communist_track -= 1
                    self.state.block_next_communist_power = True

        if emergency is True:
            if policy_type == "article48":
                # President executes Article 48 powers
                print(
                    f"President {self.state.president.name} executed Article 48 powers."
                )
            elif policy_type == "enablingact":
                # Chancellor executes Enabling Act powers
                print(
                    f"Chancellor {self.state.chancellor.name} executed Enabling Act powers."
                )

        # Store the most recently enacted policy
        self.state.most_recent_policy = policy

        # Track the policy enactment for statistics
        if not hasattr(self.state, "policy_history"):
            self.state.policy_history = []
        # Record this policy enactment
        self.state.policy_history.append(
            {
                "policy": policy_type,
                "president": self.state.president,
                "chancellor": self.state.chancellor,
                "round": self.state.round_number,
                "liberal_track": self.state.board.liberal_track,
                "fascist_track": self.state.board.fascist_track,
                "communist_track": (
                    self.communist_track if self.with_communists else 0
                ),
            }
        )
        self.state.enacted_policies += 1

        return power

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

        return self.get_power_for_track_position(
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

        return self.get_power_for_track_position(
            "communist", self.state.board.communist_track
        )

    def get_power_for_track_position(self, track_type, position):
        """
        Get the power at a specific position on a track

        Args:
            track_type: The type of track ("fascist" or "communist")
            position: The position on the track (1-indexed)

        Returns:
            str or None: The power at that position
        """
        if track_type == "fascist":
            if 1 <= position <= len(self.fascist_powers):
                return self.fascist_powers[position - 1]
        elif track_type == "communist":
            if 1 <= position <= len(self.communist_powers):
                return self.communist_powers[position - 1]

        return None
