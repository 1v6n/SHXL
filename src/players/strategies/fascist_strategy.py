from random import choice, random

from src.players.strategies.base_strategy import PlayerStrategy


class FascistStrategy(PlayerStrategy):
    """Strategy for fascist players"""

    def nominate_chancellor(self, eligible_players):
        """Choose Hitler or another fascist if possible"""
        # Debug: print all eligible players and their attributes
        print(f"DEBUG: nominate_chancellor eligible_players:")
        for p in eligible_players:
            print(
                f"  Player {getattr(p, 'id', 'UNKNOWN')}: is_fascist={getattr(p, 'is_fascist', 'MISSING')}, is_hitler={getattr(p, 'is_hitler', 'MISSING')}"
            )
        print(f"DEBUG: fascist_track = {self.player.state.fascist_track}")

        # If Hitler can be chancellor and enough fascist policies are enacted
        if self.player.state.fascist_track >= 3 and any(
            getattr(p, "is_hitler", False) for p in eligible_players
        ):
            # Choose Hitler
            for player in eligible_players:
                if getattr(player, "is_hitler", False):
                    print(
                        f"DEBUG: Choosing Hitler player {getattr(player, 'id', 'UNKNOWN')}"
                    )
                    return player

        # Otherwise prefer fellow fascists
        fascists = [
            p
            for p in eligible_players
            if getattr(p, "is_fascist", False) and not getattr(p, "is_hitler", False)
        ]
        print(f"DEBUG: Found {len(fascists)} non-Hitler fascist players")
        if fascists:
            chosen = choice(fascists)
            print(
                f"DEBUG: Choosing non-Hitler fascist player {getattr(chosen, 'id', 'UNKNOWN')}"
            )
            return chosen

        # If no fascists are eligible, choose randomly
        chosen = choice(eligible_players)
        print(
            f"DEBUG: No fascists found, choosing random player {getattr(chosen, 'id', 'UNKNOWN')}"
        )
        return chosen

    def filter_policies(self, policies):
        """Keep fascist policies if possible"""
        # Sort policies by preference: fascist > communist > liberal
        sorted_policies = sorted(
            policies,
            key=lambda p: (
                1 if p.type == "fascist" else (0.5 if p.type == "communist" else 0)
            ),
            reverse=True,
        )

        # Keep the two best policies
        chosen = sorted_policies[:2]
        discarded = sorted_policies[2]

        return chosen, discarded

    def choose_policy(self, policies):
        """Enact fascist policy if possible"""
        # Sort by preference: fascist > communist > liberal
        sorted_policies = sorted(
            policies,
            key=lambda p: (
                1 if p.type == "fascist" else (0.5 if p.type == "communist" else 0)
            ),
            reverse=True,
        )

        # Choose the best policy
        chosen = sorted_policies[0]
        discarded = sorted_policies[1]

        return chosen, discarded

    def vote(self, president, chancellor):
        """Vote Yes if chancellor is fascist or Hitler"""
        if chancellor.is_fascist:
            return True

        # If chancellor or president is a known liberal, be more cautious
        chancellor_known_liberal = (
            chancellor.id in self.player.inspected_players
            and self.player.inspected_players[chancellor.id] == "liberal"
        )
        president_known_liberal = (
            president.id in self.player.inspected_players
            and self.player.inspected_players[president.id] == "liberal"
        )

        # If both are known liberals, be more likely to vote no
        if chancellor_known_liberal and president_known_liberal:
            return random() <= 0.3

        # If a fascist policy would result in a power that could help fascists, vote yes
        if (
            self.player.state.fascist_track == 2  # Next would be investigate
            or self.player.state.fascist_track == 4
        ):  # Next would be execution
            return random() <= 0.8

        # Otherwise, vote randomly with a bias toward yes
        return random() <= 0.7

    def veto(self, policies):
        """Veto if no fascist policies available"""
        fascist_policies = [p for p in policies if p.type == "fascist"]
        return not fascist_policies

    def accept_veto(self, policies):
        """Accept veto if no fascist policies available"""
        fascist_policies = [p for p in policies if p.type == "fascist"]
        return not fascist_policies

    def choose_player_to_kill(self, eligible_players):
        """Kill liberals or communists (not fascists)"""
        # If game is close to liberal victory, prioritize killing known liberals
        liberal_track = self.player.state.board.liberal_track
        liberal_track_size = self.player.state.board.liberal_track_size

        # Track known players by party
        known_liberals = []
        known_communists = []
        unknown_players = []
        suspected_liberals = []

        # Categorize players based on knowledge
        for p in eligible_players:
            # Skip fellow fascists
            if p.is_fascist:
                continue  # Check if we've inspected them
            if p.id in self.player.inspected_players:
                if self.player.inspected_players[p.id] == "liberal":
                    known_liberals.append(p)
                elif self.player.inspected_players[p.id] == "communist":
                    known_communists.append(p)
            # If we haven't inspected them directly
            elif (
                hasattr(self.player, "known_affiliations")
                and p.id in self.player.known_affiliations
            ):
                if self.player.known_affiliations[p.id] == "liberal":
                    known_liberals.append(p)
                elif self.player.known_affiliations[p.id] == "communist":
                    known_communists.append(p)
            else:
                # Check voting patterns for suspicion
                # Players who frequently vote against fascist governments might be liberals
                unknown_players.append(p)

        # Always prioritize known liberals for execution (they are the main enemy)
        if known_liberals:
            return choice(known_liberals)

        # If liberals are close to winning and we don't have known liberals, be more aggressive
        if liberal_track >= liberal_track_size - 2 and suspected_liberals:
            return choice(suspected_liberals)

        # If communists are in play and known, they're also a threat
        if known_communists:
            return choice(known_communists)

        # If no known targets, kill a suspected liberal or random non-fascist
        if suspected_liberals:
            return choice(suspected_liberals)
        elif unknown_players:
            return choice(unknown_players)

        # As a last resort, choose any eligible player
        non_fascists = [p for p in eligible_players if not p.is_fascist]
        if non_fascists:
            return choice(non_fascists)

        return choice(eligible_players)

    def choose_player_to_inspect(self, eligible_players):
        """Inspect non-fascists strategically"""
        # Filter out fascists and already inspected players
        uninspected = [
            p
            for p in eligible_players
            if not p.is_fascist and p.id not in self.player.inspected_players
        ]

        if uninspected:
            return choice(uninspected)

        # If all players have been inspected or are fascists, inspect any non-fascist
        non_fascists = [p for p in eligible_players if not p.is_fascist]
        if non_fascists:
            return choice(non_fascists)

        return choice(eligible_players)

    def choose_next_president(self, eligible_players):
        """Choose fascist as next president if possible"""
        fascists = [p for p in eligible_players if p.is_fascist and not p.is_hitler]

        if fascists:
            return choice(fascists)

        # If no fascists available, choose a player who's not known to be liberal
        unknown_players = [
            p
            for p in eligible_players
            if p.id not in self.player.inspected_players
            or self.player.inspected_players[p.id] != "liberal"
        ]

        if unknown_players:
            return choice(unknown_players)

        return choice(eligible_players)

    def choose_player_to_radicalize(self, eligible_players):
        """Choose a liberal to radicalize"""
        # Try to radicalize a known liberal
        liberals = [
            p
            for p in eligible_players
            if (
                p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            )
        ]

        if liberals:
            return choice(liberals)

        # Otherwise choose someone who's not a fascist and not Hitler
        non_fascist_non_hitler = [
            p for p in eligible_players if not p.is_fascist and not p.is_hitler
        ]

        if non_fascist_non_hitler:
            return choice(non_fascist_non_hitler)

        return choice(eligible_players)

    def choose_player_to_mark(self, eligible_players):
        """Choose a player to mark for execution"""
        # Same logic as choosing to kill
        return self.choose_player_to_kill(eligible_players)

    def choose_player_to_bug(self, eligible_players):
        """Choose a player to bug (view party membership)"""
        # Prioritize non-fascists that haven't been inspected
        uninspected_non_fascists = [
            p
            for p in eligible_players
            if not p.is_fascist and p.id not in self.player.inspected_players
        ]

        if uninspected_non_fascists:
            return choice(uninspected_non_fascists)

        # If all non-fascists inspected, choose any non-fascist
        non_fascists = [p for p in eligible_players if not p.is_fascist]
        if non_fascists:
            return choice(non_fascists)

        return choice(eligible_players)

    def propaganda_decision(self, policy):
        """Decide whether to discard the top policy"""
        # Keep fascist policies, discard liberal ones
        if policy.type == "liberal":
            return True
        elif policy.type == "fascist":
            return False
        # For other types, make a strategic decision
        return choice([True, False])

    def choose_revealer(self, eligible_players):
        """Choose a player to reveal party membership to (Impeachment)"""
        # Debug: print all eligible players and their attributes
        print(f"DEBUG: choose_revealer eligible_players:")
        for p in eligible_players:
            print(
                f"  Player {getattr(p, 'id', 'UNKNOWN')}: is_fascist={getattr(p, 'is_fascist', 'MISSING')}, is_hitler={getattr(p, 'is_hitler', 'MISSING')}"
            )

        # Choose a fellow fascist if possible
        fascists = [p for p in eligible_players if getattr(p, "is_fascist", False)]
        print(f"DEBUG: Found {len(fascists)} fascist players")
        if fascists:
            chosen = choice(fascists)
            print(f"DEBUG: Choosing fascist player {getattr(chosen, 'id', 'UNKNOWN')}")
            return chosen

        # Otherwise choose randomly
        chosen = choice(eligible_players)
        print(
            f"DEBUG: No fascists found, choosing random player {getattr(chosen, 'id', 'UNKNOWN')}"
        )
        return chosen

    def pardon_player(self):
        """Decide whether to pardon a player marked for execution"""
        if (
            not hasattr(self.player.state, "marked_for_execution")
            or not self.player.state.marked_for_execution
        ):
            return False

        marked_player = self.player.state.marked_for_execution

        # Always pardon Hitler
        if marked_player.is_hitler:
            return True

        # Pardon fellow fascists
        if marked_player.is_fascist:
            return True

        # Don't pardon liberals/communists
        return False

    def chancellor_veto_proposal(self, policies):
        """Decide whether to propose a veto as chancellor"""
        # Propose veto if no fascist policies available
        fascist_policies = [p for p in policies if p.type == "fascist"]
        return len(fascist_policies) == 0

    def vote_of_no_confidence(self):
        """Decide whether to enact the discarded policy (Vote of No Confidence)"""
        if (
            not hasattr(self.player.state, "last_discarded")
            or not self.player.state.last_discarded
        ):
            return False

        # Enact if it's a fascist policy
        if self.player.state.last_discarded.type == "fascist":
            return True
        # Don't enact liberal policies
        elif self.player.state.last_discarded.type == "liberal":
            return False
        # Consider communist policies
        return choice([True, False])

    def social_democratic_removal_choice(self):
        """Choose which policy track to remove from (Social Democratic)"""
        # Remove from communist track if possible, then liberal
        if self.player.state.communist_track > 0:
            return "communist"
        elif self.player.state.liberal_track > 0:
            return "liberal"
        else:
            return choice(["liberal", "communist"])
