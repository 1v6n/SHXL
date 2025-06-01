from random import randint

from src.game.board import GameBoard
from src.game.game_state import EnhancedGameState
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
        self.current_phase = None
        self.state = EnhancedGameState()
        self.communists_in_play = False
        self.anti_policies_in_play = False
        self.emergency_powers_in_play = False
        self.human_player_indices = []  # Initialize human player indices
        self.ai_strategy = "smart"  # Default to smart strategy for AI players
        self.player_count = 0  # Initialize player_count attribute
        self.hitler_player = None  # Initialize hitler_player attribute

    def setup_game(
        self,
        player_count,
        with_communists=True,
        with_anti_policies=False,
        with_emergency_powers=False,
        human_player_indices=None,
        ai_strategy="smart",
    ):
        """Add commentMore actions
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
            # Add tracking structures for government history and policy enactmentsAdd commentMore actions
            self.state.government_history = []
            self.state.policy_history = []
            # Set up the boardAdd commentMore actions
            self.initialize_board(self.player_count, self.communists_in_play)
            # Create the policy deckAdd commentMore actions
            policy_factory = PolicyFactory()
            self.state.board.initialize_policy_deck(
                policy_factory, with_anti_policies, with_emergency_powers
            )
            self.assign_players()
            self.inform_players()
            self.choose_first_president()
            # Enter the election phaseAdd commentMore actions
            self.current_phase = None

    def initialize_board(self, players, communist_flag):
        """Initialize the game board"""
        self.state.board = GameBoard(self.state, players, communist_flag)

    def start_game(self):
        """
        Run the game from beginning to end
        Returns:Add commentMore actions
            str: The winner of the game
        """
        # Run phases until game is overAdd commentMore actions
        while not self.state.game_over:
            self.current_phase = self.current_phase.execute()

        # Return the winnerAdd commentMore actions
        return self.state.winner

    def assign_players(self):
        """
        Create players and assign rolesAdd commentMore actions
        Uses the player factory to create players
        Uses the role factory to create roles
        """
        # Create playersAdd commentMore actions
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
        self.state.president_candidate = self.state.active_players[random_index]
