from abc import ABC, abstractmethod


class PlayerStrategy(ABC):
    """Base class for player strategies"""

    def __init__(self, player):
        self.player = player

    @abstractmethod
    def nominate_chancellor(self, eligible_players):
        """Choose a chancellor from eligible players"""

    @abstractmethod
    def filter_policies(self, policies):
        """Choose which policies to pass as president"""

    @abstractmethod
    def choose_policy(self, policies):
        """Choose which policy to enact as chancellor"""

    @abstractmethod
    def vote(self, president, chancellor):
        """Vote on a government"""

    @abstractmethod
    def veto(self, policies):
        """Decide whether to veto"""

    @abstractmethod
    def accept_veto(self, policies):
        """Decide whether to accept veto"""

    @abstractmethod
    def choose_player_to_kill(self, eligible_players):
        """Choose a player to execute"""

    @abstractmethod
    def choose_player_to_inspect(self, eligible_players):
        """Choose a player to inspect"""

    @abstractmethod
    def choose_next_president(self, eligible_players):
        """Choose the next president"""

    @abstractmethod
    def choose_player_to_radicalize(self, eligible_players):
        """Choose a player to convert to communist"""

    @abstractmethod
    def choose_player_to_mark(self, eligible_players):
        """Choose a player to mark for execution"""

    @abstractmethod
    def choose_player_to_bug(self, eligible_players):
        """Choose a player to bug (view party membership)"""

    @abstractmethod
    def propaganda_decision(self, policy):
        """Decide whether to discard the top policy"""

    @abstractmethod
    def choose_revealer(self, eligible_players):
        """Choose a player to reveal party membership to (Impeachment)"""

    @abstractmethod
    def pardon_player(self):
        """Decide whether to pardon a player marked for execution"""

    @abstractmethod
    def chancellor_veto_proposal(self, policies):
        """Decide whether to propose a veto as chancellor"""

    @abstractmethod
    def vote_of_no_confidence(self):
        """Decide whether to enact the discarded policy (Vote of No Confidence)"""

    @abstractmethod
    def social_democratic_removal_choice(self):
        """Choose which policy track to remove from (Social Democratic)"""
