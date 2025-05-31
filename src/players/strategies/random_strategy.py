from random import choice, random

from src.players.strategies.base_strategy import PlayerStrategy


class RandomStrategy(PlayerStrategy):
    """Strategy that makes random decisions"""

    def nominate_chancellor(self, eligible_players):
        """Choose a random eligible player as chancellor"""
        return choice(eligible_players)

    def filter_policies(self, policies):
        """Discard a random policy without removing all duplicates"""
        discard = choice(policies)
        chosen = policies.copy()
        chosen.remove(discard)  # removes only one occurrence
        return chosen, discard

    def choose_policy(self, policies):
        """Enact a random policy"""
        chosen = choice(policies)
        discarded = [p for p in policies if p != chosen][0]
        return chosen, discarded

    def vote(self, president, chancellor):
        """Vote randomly"""
        return random() >= 0.5

    def veto(self, policies):
        """Veto randomly (20% chance)"""
        return random() <= 0.2

    def accept_veto(self, policies):
        """Accept veto randomly (20% chance)"""
        return random() <= 0.2

    def choose_player_to_kill(self, eligible_players):
        """Choose a random player to kill"""
        return choice(eligible_players)

    def choose_player_to_inspect(self, eligible_players):
        """Choose a random player to inspect"""
        return choice(eligible_players)

    def choose_next_president(self, eligible_players):
        """Choose a random player as next president"""
        return choice(eligible_players)

    def choose_player_to_radicalize(self, eligible_players):
        """Choose a random player to radicalize"""
        return choice(eligible_players)

    def choose_player_to_mark(self, eligible_players):
        """Choose a random player to mark for execution"""
        return choice(eligible_players)

    def choose_player_to_bug(self, eligible_players):
        """Choose a random player to bug"""
        return choice(eligible_players)

    def propaganda_decision(self, policy):
        """Randomly decide whether to discard the top policy"""
        return random() <= 0.5

    def choose_revealer(self, eligible_players):
        """Choose a random player to reveal party membership to"""
        return choice(eligible_players)

    def pardon_player(self):
        """Randomly decide whether to pardon a player"""
        return random() <= 0.5

    def chancellor_veto_proposal(self, policies):
        """Randomly decide whether to propose a veto as chancellor"""
        return random() <= 0.2

    def vote_of_no_confidence(self):
        """Randomly decide whether to enact the discarded policy"""
        return random() <= 0.5

    def social_democratic_removal_choice(self):
        """Randomly choose which policy track to remove from"""
        return choice(["fascist", "communist"])
