from abc import ABC, abstractmethod


class Player(ABC):
    """Enhanced player class to support all SHXL features"""

    def __init__(self, player_id, name, role, state):
        self.player_id = player_id
        self.name = name
        self.role = role
        self.state = state
        self.is_dead = False
        self.player_count = (
            len(state.players) if hasattr(state, "players") and state.players else 0
        )

        # Knowledge
        self.hitler = None  # Will be set if fascist
        self.fascists = None  # Will be set if fascist
        self.known_communists = []  # Will be set if communist
        self.inspected_players = {}  # Player ID -> party membership
        self.known_affiliations = {}  # Player ID -> party membership

    @property
    def is_fascist(self):
        """Check if player is fascist"""
        return self.role.party_membership == "fascist"

    @property
    def is_liberal(self):
        """Check if player is liberal"""
        return self.role.party_membership == "liberal"

    @property
    def is_communist(self):
        """Check if player is communist"""
        return self.role.party_membership == "communist"

    @property
    def is_hitler(self):
        """Check if player is Hitler"""
        return self.role.role == "hitler"

    @property
    def knows_hitler(self):
        """Check if player knows who Hitler is"""
        return self.hitler is not None

    def __repr__(self):
        return f"Player id:{self.player_id}, name:{self.name}, role:{self.role}"

    def initialize_role_attributes(self):
        """Initialize attributes based on the assigned role"""
        if self.role is None:
            return

        # Get player count from the game state
        player_count = (
            len(self.state.players)
            if hasattr(self.state, "players") and self.state.players
            else 0
        )

        # Initialize role-specific attributes
        if self.is_fascist and not self.is_hitler:
            self.fascists = []
            self.hitler = None
        elif self.is_hitler and player_count < 8:
            self.fascists = []
        elif self.is_communist and player_count < 11:
            self.known_communists = []

    # Required methods

    @abstractmethod
    def nominate_chancellor(self):
        """
        Choose a chancellor

        Returns:
            player: The nominated chancellor
        """

    @abstractmethod
    def filter_policies(self, policies):
        """
        Choose which policies to pass as president

        Args:
            policies: List of 3 policies

        Returns:
            tuple: (chosen [2], discarded [1])
        """

    @abstractmethod
    def choose_policy(self, policies):
        """
        Choose which policy to enact as chancellor

        Args:
            policies: List of 2 policies

        Returns:
            tuple: (chosen [1], discarded [1])
        """

    @abstractmethod
    def vote(self):
        """
        Vote on a government

        Returns:
            bool: True for Ja, False for Nein
        """

    @abstractmethod
    def veto(self):
        """
        Decide whether to veto (as chancellor)

        Returns:
            bool: True to veto, False otherwise
        """

    @abstractmethod
    def accept_veto(self):
        """
        Decide whether to accept veto (as president)

        Returns:
            bool: True to accept veto, False otherwise
        """

    @abstractmethod
    def view_policies(self, policies):
        """
        React to seeing policies with Policy Peek

        Args:
            policies: List of policies
        """

    @abstractmethod
    def kill(self):
        """
        Choose a player to execute

        Returns:
            player: The chosen player
        """

    @abstractmethod
    def choose_player_to_mark(self):
        """
        Choose a player to mark

        Returns:
            player: The chosen player
        """

    @abstractmethod
    def inspect_player(self):
        """
        Choose a player to inspect

        Returns:
            player: The chosen player
        """

    @abstractmethod
    def choose_next(self):
        """
        Choose the next president (special election)

        Returns:
            player: The chosen player
        """

    # Communist-specific methods

    @abstractmethod
    def choose_player_to_radicalize(self):
        """
        Choose a player to convert to communist

        Returns:
            player: The chosen player
        """

    # Emergency power methods

    @abstractmethod
    def propaganda_decision(self, policy):
        """
        Decide whether to discard the top policy

        Args:
            policy: The top policy

        Returns:
            bool: True to discard, False to keep
        """

    @abstractmethod
    def choose_revealer(self, eligible_players):
        """
        Choose a player to reveal party membership to (Impeachment)

        Returns:
            player: The chosen player
        """

    @abstractmethod
    def social_democratic_removal_choice(self, state):
        """
        Choose which policy track to remove from (Social Democratic)

        Returns:
            str: "fascist" or "communist"
        """
