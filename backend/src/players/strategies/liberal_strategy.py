from random import choice, random

from src.players.strategies.base_strategy import PlayerStrategy


class LiberalStrategy(PlayerStrategy):
    """Strategy for liberal players"""

    def nominate_chancellor(self, eligible_players):
        """Choose player that is not suspected to be fascist"""
        # Prioritize players we trust (known liberals)
        trusted_players = [
            p
            for p in eligible_players
            if p.id in self.player.inspected_players
            and self.player.inspected_players[p.id] == "liberal"
        ]

        if trusted_players:
            return choice(trusted_players)

        # Next priority: avoid suspected fascists
        suspected_fascists = [
            p
            for p in eligible_players
            if p.id in self.player.inspected_players
            and self.player.inspected_players[p.id] == "fascist"
        ]

        non_suspected = [p for p in eligible_players if p not in suspected_fascists]

        if non_suspected:
            return choice(non_suspected)

        return choice(eligible_players)

    def filter_policies(self, policies):
        """Keep liberal policies if possible"""
        # Sort policies by preference: liberal > communist > fascist
        sorted_policies = sorted(
            policies,
            key=lambda p: (
                1 if p.type == "liberal" else (0.5 if p.type == "communist" else 0)
            ),
            reverse=True,
        )

        # Keep the two best policies
        chosen = sorted_policies[:2]
        discarded = sorted_policies[2]

        return chosen, discarded

    def choose_policy(self, policies):
        """Enact liberal policy if possible"""
        # Sort by preference: liberal > communist > fascist
        sorted_policies = sorted(
            policies,
            key=lambda p: (
                1 if p.type == "liberal" else (0.5 if p.type == "communist" else 0)
            ),
            reverse=True,
        )

        # Choose the best policy
        chosen = sorted_policies[0]
        discarded = sorted_policies[1]

        return chosen, discarded

    def vote(self, president, chancellor):
        """Vote based on trust and suspicion"""
        # Vote yes if both are trusted
        president_trusted = (
            president.id in self.player.inspected_players
            and self.player.inspected_players[president.id] == "liberal"
        )
        chancellor_trusted = (
            chancellor.id in self.player.inspected_players
            and self.player.inspected_players[chancellor.id] == "liberal"
        )

        if president_trusted and chancellor_trusted:
            return True

        # Vote no if chancellor is suspected fascist
        chancellor_suspected = (
            chancellor.id in self.player.inspected_players
            and self.player.inspected_players[chancellor.id] == "fascist"
        )

        if chancellor_suspected:
            return False

        # If chancellor could be Hitler and 3+ fascist policies are enacted, be very cautious
        if self.player.state.fascist_track >= 3:
            # If chancellor is unknown and could be Hitler, more likely to vote no
            if chancellor.id not in self.player.inspected_players:
                return random() <= 0.3
            # Otherwise be somewhat cautious
            return random() <= 0.5
        else:
            # Early game, more willing to trust unknown players
            return random() <= 0.7

    def veto(self, policies):
        """Veto if all policies are fascist"""
        return all(p.type == "fascist" for p in policies)

    def accept_veto(self, policies):
        """Accept veto if all policies are fascist"""
        return all(p.type == "fascist" for p in policies)

    def choose_player_to_kill(self, eligible_players):
        """Kill suspected fascists"""
        # First priority: Kill players confirmed as fascists
        confirmed_fascists = [
            p
            for p in eligible_players
            if p.id in self.player.inspected_players
            and self.player.inspected_players[p.id] == "fascist"
        ]

        if confirmed_fascists:
            return choice(confirmed_fascists)

        # Track players involved in fascist policy enactments
        suspicious_players = []
        history = []

        # Check for strong suspicions based on government activity
        # This is a simplified example - in a real implementation, we'd track each government
        # and which policies they enacted
        if hasattr(self.player.state, "government_history"):
            history = self.player.state.government_history

        # Count how many times each player was in government when fascist policies were enacted
        suspicion_counts = {}
        for p in eligible_players:
            suspicion_counts[p.id] = 0

        # In a real implementation, we'd analyze the history here
        # For this example, we'll use a simplified approach based on inspections and any available history

        # Second priority: kill players not yet inspected who might be fascists
        uninspected = [
            p for p in eligible_players if p.id not in self.player.inspected_players
        ]

        if uninspected:
            # If we have suspicion data, use it
            if suspicious_players:
                suspicious_uninspected = [
                    p for p in uninspected if p in suspicious_players
                ]
                if suspicious_uninspected:
                    return choice(suspicious_uninspected)

            # Otherwise choose randomly from uninspected
            return choice(uninspected)

        # Last resort: choose randomly from eligible players
        return choice(eligible_players)

    def choose_player_to_inspect(self, eligible_players):
        """Inspect players who haven't been inspected yet, prioritizing suspicious ones"""
        # First, get uninspected players
        uninspected = [
            p for p in eligible_players if p.id not in self.player.inspected_players
        ]

        if uninspected:
            # If we have suspicious players, prioritize them
            suspicious_uninspected = []

            # In a real implementation, we'd have more sophisticated suspicion tracking
            # For now, this is a placeholder for that logic

            if suspicious_uninspected:
                return choice(suspicious_uninspected)

            # If no suspicious players or no data, choose randomly from uninspected
            return choice(uninspected)

        # If all have been inspected, choose randomly
        return choice(eligible_players)

    def choose_next_president(self, eligible_players):
        """Choose trusted liberal as next president if possible"""
        trusted_liberals = [
            p
            for p in eligible_players
            if p.id in self.player.inspected_players
            and self.player.inspected_players[p.id] == "liberal"
        ]

        if trusted_liberals:
            return choice(trusted_liberals)

        # Otherwise, choose someone who hasn't been confirmed as fascist
        non_fascists = [
            p
            for p in eligible_players
            if p.id not in self.player.inspected_players
            or self.player.inspected_players[p.id] != "fascist"
        ]

        if non_fascists:
            return choice(non_fascists)

        return choice(eligible_players)

    def choose_player_to_radicalize(self, eligible_players):
        """Choose a suspected fascist to neutralize"""
        suspected_fascists = [
            p
            for p in eligible_players
            if p.id in self.player.inspected_players
            and self.player.inspected_players[p.id] == "fascist"
            and not p.is_hitler
        ]  # Can't convert Hitler

        if suspected_fascists:
            return choice(suspected_fascists)

        # If no confirmed fascists, try someone suspicious but not confirmed
        suspicious_players = []

        # In a real implementation, we'd have more sophisticated suspicion tracking
        # based on government history and voting patterns

        if suspicious_players:
            eligible_suspicious = [
                p
                for p in suspicious_players
                if p in eligible_players and not p.is_hitler
            ]
            if eligible_suspicious:
                return choice(eligible_suspicious)

        # Last resort: choose randomly
        return choice(eligible_players)

    def choose_player_to_mark(self, eligible_players):
        """Choose a player to mark for execution"""
        # Same logic as choosing to kill
        return self.choose_player_to_kill(eligible_players)

    def choose_player_to_bug(self, eligible_players):
        """Choose a player to bug (view party membership)"""
        # Prioritize uninspected players
        uninspected = [
            p for p in eligible_players if p.id not in self.player.inspected_players
        ]

        if uninspected:
            return choice(uninspected)

        # If all inspected, choose randomly
        return choice(eligible_players)

    def propaganda_decision(self, policy):
        """Decide whether to discard the top policy"""
        # Discard fascist policies, keep liberal ones
        if policy.type == "fascist":
            return True
        elif policy.type == "liberal":
            return False
        # For other types, make a random decision
        return choice([True, False])

    def choose_revealer(self, eligible_players):
        """Choose a player to reveal party membership to (Impeachment)"""
        # Choose a trusted liberal if known
        trusted_liberals = [
            p
            for p in eligible_players
            if p.id in self.player.inspected_players
            and self.player.inspected_players[p.id] == "liberal"
        ]

        if trusted_liberals:
            return choice(trusted_liberals)

        # Otherwise choose randomly
        return choice(eligible_players)

    def pardon_player(self):
        """Decide whether to pardon a player marked for execution"""
        if (
            not hasattr(self.player.state, "marked_for_execution")
            or not self.player.state.marked_for_execution
        ):
            return False

        marked_player = self.player.state.marked_for_execution

        # Pardon if we know they're liberal
        if (
            marked_player.id in self.player.inspected_players
            and self.player.inspected_players[marked_player.id] == "liberal"
        ):
            return True

        # Don't pardon if we know they're fascist
        if (
            marked_player.id in self.player.inspected_players
            and self.player.inspected_players[marked_player.id] == "fascist"
        ):
            return False

        # Random decision for unknowns, slight bias toward pardoning
        return choice([True, True, False])

    def chancellor_veto_proposal(self, policies):
        """Decide whether to propose a veto as chancellor"""
        # Propose veto if all policies are fascist
        return all(p.type == "fascist" for p in policies)

    def vote_of_no_confidence(self):
        """Decide whether to enact the discarded policy (Vote of No Confidence)"""
        if (
            not hasattr(self.player.state, "last_discarded")
            or not self.player.state.last_discarded
        ):
            return False

        # Enact if it's a liberal policy
        if self.player.state.last_discarded.type == "liberal":
            return True
        # Don't enact fascist policies
        elif self.player.state.last_discarded.type == "fascist":
            return False
        # Random for other types
        return choice([True, False])

    def social_democratic_removal_choice(self):
        """Choose which policy track to remove from (Social Democratic)"""
        # Always remove from fascist track if possible
        if self.player.state.fascist_track > 0:
            return "fascist"
        elif self.player.state.communist_track > 0:
            return "communist"
        else:
            return choice(["fascist", "communist"])
