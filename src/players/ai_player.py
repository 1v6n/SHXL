from random import choice

from src.players.abstract_player import Player
from src.players.strategies import (
    CommunistStrategy,
    FascistStrategy,
    LiberalStrategy,
    RandomStrategy,
    SmartStrategy,
)


class AIPlayer(Player):
    """AI player that uses a strategy to make decisions"""

    def __init__(self, id, name, role, state, strategy_type="role"):
        super().__init__(id, name, role, state)
        self.peeked_policies = None  # Initialize attribute

        # Handle string roles for testing purposes
        if isinstance(role, str):
            from src.roles.role import Communist, Fascist, Hitler, Liberal

            if role == "liberal":
                role = Liberal()
            elif role == "fascist":
                role = Fascist()
            elif role == "communist":
                role = Communist()
            elif role == "hitler":
                role = Hitler()
            self.role = role

        # No puede determinar estrategia si no hay rol asignado
        if role is None:
            self.strategy = RandomStrategy(self)  # default temporal
            return

        # pick strategy
        if strategy_type == "random":
            self.strategy = RandomStrategy(self)
        elif strategy_type == "smart":
            self.strategy = SmartStrategy(self)
        else:  # "role" or anything else
            if self.is_fascist or self.is_hitler:
                self.strategy = FascistStrategy(self)
            elif self.is_communist:
                self.strategy = CommunistStrategy(self)
            else:
                self.strategy = LiberalStrategy(self)

    def nominate_chancellor(self, eligible_players=None):
        """
        Choose a chancellor

        Returns:
            player: The nominated chancellor
        """
        if eligible_players is None:
            eligible_players = self.state.get_eligible_chancellors()
        return self.strategy.nominate_chancellor(eligible_players)

    def filter_policies(self, policies):
        """
        Choose which policies to pass as president

        Args:
            policies: List of 3 policies

        Returns:
            tuple: (chosen [2], discarded [1])
        """
        return self.strategy.filter_policies(policies)

    def choose_policy(self, policies):
        """
        Choose which policy to enact as chancellor

        Args:
            policies: List of 2 policies

        Returns:
            tuple: (chosen [1], discarded [1])
        """
        return self.strategy.choose_policy(policies)

    def vote(self):
        """
        Vote on a government

        Returns:
            bool: True for Ja, False for Nein
        """
        return self.strategy.vote(
            self.state.president_candidate, self.state.chancellor_candidate
        )

    def veto(self):
        """
        Decide whether to veto (as chancellor)

        Returns:
            bool: True to veto, False otherwise
        """
        # Get policies from game state, simplified here
        policies = self.state.current_policies
        return self.strategy.veto(policies)

    def accept_veto(self):
        """
        Decide whether to accept veto (as president)

        Returns:
            bool: True to accept veto, False otherwise
        """
        # Get policies from game state, simplified here
        policies = self.state.current_policies
        return self.strategy.accept_veto(policies)

    def view_policies(self, policies):
        """
        React to seeing policies with Policy Peek

        Args:
            policies: List of policies
        """
        # Just remember the policies, no direct action
        self.peeked_policies = policies

    def kill(self):
        """
        Choose a player to execute

        Returns:
            player: The chosen player
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_kill(eligible_players)

    def choose_player_to_mark(self):
        """
        Choose a player to mark for execution

        Returns:
            player: The chosen player
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_mark(eligible_players)

    def inspect_player(self):
        """
        Choose a player to inspect

        Returns:
            player: The chosen player
        """
        uninspected = [
            p
            for p in self.state.active_players
            if p != self and p.id not in self.inspected_players
        ]

        # If all players have been inspected, can inspect any player
        eligible_players = (
            uninspected
            if uninspected
            else [p for p in self.state.active_players if p != self]
        )
        return self.strategy.choose_player_to_inspect(eligible_players)

    def choose_next(self):
        """
        Choose the next president (special election)

        Returns:
            player: The chosen player
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_next_president(eligible_players)

    def choose_player_to_radicalize(self):
        """
        Choose a player to convert to communist

        Returns:
            player: The chosen player
        """
        # Cannot radicalize Hitler or self
        eligible_players = [
            p for p in self.state.active_players if p != self and not p.is_hitler
        ]
        return self.strategy.choose_player_to_radicalize(eligible_players)

    def propaganda_decision(self, policy):
        """
        Decide whether to discard the top policy

        Args:
            policy: The top policy

        Returns:
            bool: True to discard, False to keep
        """
        # Discard based on role
        if self.is_liberal:
            return policy.type == "fascist"
        elif self.is_fascist or self.is_hitler:
            return policy.type == "liberal"
        elif self.is_communist:
            return policy.type == "fascist"
        else:
            return False

    def choose_revealer(self, eligible_players):
        """
        Choose a player to reveal party membership to (Impeachment)

        Returns:
            player: The chosen player
        """
        # Choose a trusted player based on role
        if self.is_liberal:
            # Choose another liberal if known
            liberals = [
                p
                for p in eligible_players
                if p != self
                and p.id in self.inspected_players
                and self.inspected_players[p.id] == "liberal"
            ]
            if liberals:
                return choice(liberals)
        elif self.is_fascist or self.is_hitler:
            # Choose a fascist if known
            fascists = [
                p for p in self.state.active_players if p != self and p.is_fascist
            ]
            if fascists:
                return choice(fascists)
        elif self.is_communist:
            # Choose a communist if known
            communists = [
                p
                for p in self.state.active_players
                if p != self and p.id in self.known_communists
            ]
            if communists:
                return choice(communists)

        # Default: choose random player
        eligible_players = [p for p in self.state.active_players if p != self]
        return choice(eligible_players)

    def social_democratic_removal_choice(self, state):
        """
        Choose which policy track to remove from (Social Democratic)

        Returns:
            str: "fascist" or "communist"
        """
        if (self.is_liberal or self.is_communist) and state.fascist_track > 0:
            # Liberals and communists want to remove fascist policies
            return "fascist"
        elif (self.is_fascist or self.is_hitler) and state.communist_track > 0:
            # Fascists want to remove communist policies
            return "communist"
        else:
            # Default
            return choice(["fascist", "communist"])

    def pardon_player(self):
        """
        Decide whether to pardon a player marked for execution

        Returns:
            bool: True to pardon, False to not pardon
        """
        if not hasattr(self.strategy, "pardon_player"):
            # Fallback for strategies without pardon implementation
            # Fascists will pardon Hitler, others are random
            if (
                (self.is_fascist or self.is_hitler)
                and self.state.marked_for_execution is not None
                and self.state.marked_for_execution.is_hitler
            ):
                return True
            return False  # Use the strategy's pardon decision
        return self.strategy.pardon_player()

    def choose_player_to_bug(self, eligible_players):
        """
        Choose a player to bug (view party membership)

        Returns:
            player: The chosen player
        """
        return self.strategy.choose_player_to_bug(eligible_players)

    def mark_for_execution(self, eligible_players=None):
        """
        Choose a player to mark for execution

        Args:
            eligible_players: List of players that can be marked (optional)

        Returns:
            player: The chosen player
        """
        if eligible_players is None:
            eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_mark(eligible_players)

    def chancellor_veto_proposal(self, policies):
        """
        As Chancellor, decide whether to propose a veto when veto power is available

        Args:
            policies: List of 2 policies

        Returns:
            bool: True to propose veto, False to enact a policy
        """
        if not self.state.veto_available:
            return False
        return self.strategy.chancellor_veto_proposal(policies)

    def vote_of_no_confidence(self):
        """
        As Chancellor with Enabling Act power, decide whether to enact the discarded policy

        Returns:
            bool: True to enact the discarded policy, False to leave it
        """
        return self.strategy.vote_of_no_confidence()

    def chancellor_propose_veto(self, policies):
        """
        Chancellor proposes a veto when veto power is available

        Args:
            policies: List of 2 policies the Chancellor received

        Returns:
            bool: True to propose a veto, False otherwise
        """
        if not self.state.veto_available:
            return False
        return self.strategy.chancellor_veto_proposal(policies)

    def choose_player_to_mark_for_execution(self):
        """
        Choose a player to mark for future execution

        Returns:
            player: The player to mark
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_mark(eligible_players)

    def choose_to_pardon(self):
        """
        Choose whether to pardon the player marked for execution

        Returns:
            bool: True to pardon, False otherwise
        """
        return self.strategy.pardon_player()

    def no_confidence_decision(self):
        """
        Decide whether to enact the discarded policy (Vote of No Confidence)

        Returns:
            bool: True to enact, False otherwise
        """
        return self.strategy.vote_of_no_confidence()

    def choose_player_to_investigate(self, eligible_players):
        """
        Choose a player to investigate their party membership

        Args:
            eligible_players: List of players that can be investigated

        Returns:
            player: The player to investigate
        """
        return self.strategy.choose_player_to_inspect(eligible_players)

    def choose_next_president(self, eligible_players):
        """
        Choose the next president for a special election

        Args:
            eligible_players: List of players that can be chosen as next president

        Returns:
            player: The player to be the next president
        """
        return self.strategy.choose_next_president(eligible_players)
