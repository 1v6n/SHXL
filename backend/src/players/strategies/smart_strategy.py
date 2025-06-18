from collections import Counter
from random import choice, random

from src.players.strategies.base_strategy import PlayerStrategy


class SmartStrategy(PlayerStrategy):
    """Advanced AI strategy with more sophisticated decision making"""

    def nominate_chancellor(self, eligible_players):
        """Choose chancellor based on game state and player knowledge"""
        # Get current game state data
        fascist_policies = self.player.state.board.fascist_track
        liberal_policies = self.player.state.board.liberal_track
        round_number = self.player.state.round_number

        # If player is fascist or Hitler
        if self.player.is_fascist or self.player.is_hitler:
            # If Hitler can be elected and we've reached 3 fascist policies
            if (
                fascist_policies >= 3
                and self.player.is_hitler
                and any(p.is_fascist for p in eligible_players)
            ):
                # Find a fellow fascist to nominate
                fascists = [
                    p for p in eligible_players if p.is_fascist and not p.is_hitler
                ]
                if fascists:
                    return choice(fascists)

            # If Hitler can be chancellor and fascists have enough policies
            if fascist_policies >= 3 and not self.player.is_hitler:
                # Try to get Hitler elected if available
                hitler = next((p for p in eligible_players if p.is_hitler), None)
                if hitler:
                    return hitler

            # Otherwise prefer fascists
            fascists = [
                p
                for p in eligible_players
                if (p.is_fascist or p.is_hitler) and p.id != self.player.id
            ]
            if fascists:
                return choice(fascists)

        # If player is liberal
        elif self.player.is_liberal:
            # Prefer players confirmed as liberals
            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]
            if known_liberals:
                return choice(
                    known_liberals
                )  # Avoid players who have enacted fascist policies
            suspicious_players = set()
            if hasattr(self.player.state, "policy_history"):
                for policy_data in self.player.state.policy_history:
                    if policy_data["policy"] == "fascist":
                        if policy_data["president"] is not None:
                            suspicious_players.add(policy_data["president"].id)
                        if policy_data["chancellor"] is not None:
                            suspicious_players.add(policy_data["chancellor"].id)

            non_suspicious = [
                p for p in eligible_players if p.id not in suspicious_players
            ]
            if non_suspicious:
                return choice(non_suspicious)

        # If player is communist
        elif self.player.is_communist:
            # Prefer known communists if available
            if (
                hasattr(self.player, "known_communists")
                and self.player.known_communists
            ):
                known_communist_players = [
                    p for p in eligible_players if p.id in self.player.known_communists
                ]
                if known_communist_players:
                    return choice(known_communist_players)

            # Avoid liberals with a preference for fascists (to create chaos)
            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]

            if eligible_players:
                non_liberals = [p for p in eligible_players if p not in known_liberals]
                if non_liberals:
                    return choice(non_liberals)

        # Default to random choice if no better strategy is available
        return choice(eligible_players)

    def filter_policies(self, policies):
        """Sorts policies by priority based on role, handling duplicates intelligently."""

        # Define priority map based on player role
        if self.player.is_fascist or self.player.is_hitler:
            priority = {
                "article48": 4,
                "enablingact": 4,
                "fascist": 3,
                "communist": 2,
                "anticommunist": 2,
                "liberal": 1,
                "socialdemocratic": 1,
                "antifascist": 0,
            }
        elif self.player.is_liberal:
            priority = {
                "article48": 4,
                "enablingact": 4,
                "liberal": 3,
                "antifascist": 3,
                "socialdemocratic": 3,
                "communist": 2,
                "anticommunist": 2,
                "fascist": 1,
            }
        else:  # Communist
            priority = {
                "article48": 4,
                "enablingact": 4,
                "communist": 3,
                "antifascist": 3,
                "fascist": 2,
                "liberal": 1,
                "socialdemocratic": 1,
                "anticommunist": 0,
            }

        # Count policy types and prepare for sorting
        type_counts = Counter(p.type for p in policies)
        decorated = [
            {"policy": p, "type": p.type, "priority": priority.get(p.type, 0)}
            for p in policies
        ]

        # Handle duplicate types specially
        duplicate_type = next((t for t, c in type_counts.items() if c == 2), None)

        if duplicate_type:
            dup_priority = priority[duplicate_type]
            solo_policy = next(d for d in decorated if d["type"] != duplicate_type)

            # If duplicates are higher priority, put them first; otherwise, put them last
            def sort_key(d):
                return (
                    d["type"] == duplicate_type
                    if dup_priority < solo_policy["priority"]
                    else d["type"] != duplicate_type
                )

            decorated.sort(key=sort_key)
        else:
            # Just sort by priority
            decorated.sort(key=lambda d: d["priority"], reverse=True)

        # Take the top 2 policies, discard the rest
        sorted_policies = [d["policy"] for d in decorated]
        chosen = sorted_policies[:2]
        discarded = sorted_policies[2]
        return chosen, discarded

    def choose_policy(self, policies):
        """Choose which policy to enact based on role"""
        # Similar logic to filter_policies but for chancellor choice
        if self.player.is_fascist or self.player.is_hitler:
            # Fascists want fascist policies
            fascist_policies = [p for p in policies if p.type == "fascist"]
            if fascist_policies:
                chosen = fascist_policies[0]
                discarded = [p for p in policies if p != chosen][0]
                return chosen, discarded

            # If no fascist policies, prefer communist over liberal
            communist_policies = [p for p in policies if p.type == "communist"]
            if communist_policies:
                chosen = communist_policies[0]
                discarded = [p for p in policies if p != chosen][0]
                return chosen, discarded

        elif self.player.is_liberal:
            # Liberals want liberal policies
            liberal_policies = [p for p in policies if p.type == "liberal"]
            if liberal_policies:
                chosen = liberal_policies[0]
                discarded = [p for p in policies if p != chosen][0]
                return chosen, discarded

        elif self.player.is_communist:
            # Communists want communist policies
            communist_policies = [p for p in policies if p.type == "communist"]
            if communist_policies:
                chosen = communist_policies[0]
                discarded = [p for p in policies if p != chosen][0]
                return chosen, discarded

            # If no communist policies, prefer fascist to create chaos
            fascist_policies = [p for p in policies if p.type == "fascist"]
            if fascist_policies:
                chosen = fascist_policies[0]
                discarded = [p for p in policies if p != chosen][0]
                return chosen, discarded

        # Default if no preference found
        chosen = policies[0]
        discarded = policies[1]
        return chosen, discarded

    def vote(self, president, chancellor):
        """Vote on government based on role and game state"""
        # Game state information
        fascist_policies = self.player.state.board.fascist_track
        liberal_policies = self.player.state.board.liberal_track

        # If player is fascist or Hitler
        if self.player.is_fascist or self.player.is_hitler:
            # Always vote for fascist governments
            if chancellor.is_fascist or chancellor.is_hitler:
                return True

            # Vote for Hitler when it's safe (3+ fascist policies)
            if fascist_policies >= 3 and chancellor.is_hitler:
                return True

            # Be more cautious with unknown players
            return random() <= 0.7

        # If player is liberal
        elif self.player.is_liberal:
            # Vote for known liberals
            if (
                chancellor.id in self.player.inspected_players
                and self.player.inspected_players[chancellor.id] == "liberal"
            ):
                return True

            # Vote against known fascists
            if (
                chancellor.id in self.player.inspected_players
                and self.player.inspected_players[chancellor.id] == "fascist"
            ):
                return False

            # If we're at risk of fascist win, be more selective
            if fascist_policies >= 4:
                # Only 40% chance to approve unknown governments
                return random() <= 0.4

            # Default liberal voting - slightly more likely to approve government
            return random() <= 0.6

        # If player is communist
        elif self.player.is_communist:
            # Vote for known communists
            if (
                hasattr(self.player, "known_communists")
                and chancellor.id in self.player.known_communists
            ):
                return True

            # More likely to vote for fascist governments to create chaos
            if (
                chancellor.id in self.player.inspected_players
                and self.player.inspected_players[chancellor.id] == "fascist"
            ):
                return random() <= 0.7

            # Vote against known liberals
            if (
                chancellor.id in self.player.inspected_players
                and self.player.inspected_players[chancellor.id] == "liberal"
            ):
                return random() <= 0.3

            # Default communist voting
            return random() <= 0.5

        # Default fallback
        return random() >= 0.5

    def veto(self, policies):
        """Decide whether to propose veto based on role and policies"""
        # Count policy types
        liberal_policies = [p for p in policies if p.type == "liberal"]
        fascist_policies = [p for p in policies if p.type == "fascist"]
        communist_policies = [p for p in policies if p.type == "communist"]

        # Liberals veto if both policies are fascist
        if self.player.is_liberal and len(fascist_policies) == len(policies):
            return True

        # Fascists veto if both policies are liberal
        if (self.player.is_fascist or self.player.is_hitler) and len(
            liberal_policies
        ) == len(policies):
            return True

        # Communists veto if no communist policies and all liberal
        if (
            self.player.is_communist
            and not communist_policies
            and len(liberal_policies) == len(policies)
        ):
            return True

        # By default, rarely veto
        return random() <= 0.1

    def accept_veto(self, policies):
        """Decide whether to accept chancellor's veto"""
        # Similar logic to veto, but from president's perspective
        liberal_policies = [p for p in policies if p.type == "liberal"]
        fascist_policies = [p for p in policies if p.type == "fascist"]
        communist_policies = [p for p in policies if p.type == "communist"]

        # Check election tracker
        election_tracker = self.player.state.election_tracker

        # If election tracker is at 2, accepting veto could trigger chaos
        if election_tracker == 2:
            # Only accept in truly bad situations
            if self.player.is_liberal and len(fascist_policies) == len(policies):
                return True

            if (self.player.is_fascist or self.player.is_hitler) and len(
                liberal_policies
            ) == len(policies):
                return True

            # Otherwise don't risk chaos
            return False

        # Normal veto acceptance criteria
        if self.player.is_liberal and len(fascist_policies) == len(policies):
            return True

        if (self.player.is_fascist or self.player.is_hitler) and len(
            liberal_policies
        ) == len(policies):
            return True

        if (
            self.player.is_communist
            and not communist_policies
            and len(liberal_policies) == len(policies)
        ):
            return True

        # By default, rarely accept veto
        return random() <= 0.2

    def choose_player_to_kill(self, eligible_players):
        """Choose a player to execute based on role"""
        if self.player.is_liberal:
            # Liberals try to kill fascists
            known_fascists = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "fascist"
            ]
            if known_fascists:
                return choice(known_fascists)  # Try to kill suspicious players
            suspicious_players = set()
            if hasattr(self.player.state, "policy_history"):
                for policy_data in self.player.state.policy_history:
                    if policy_data["policy"] == "fascist":
                        if policy_data["president"] is not None:
                            suspicious_players.add(policy_data["president"].id)
                        if policy_data["chancellor"] is not None:
                            suspicious_players.add(policy_data["chancellor"].id)

            suspicious_candidates = [
                p for p in eligible_players if p.id in suspicious_players
            ]
            if suspicious_candidates:
                return choice(suspicious_candidates)

        elif self.player.is_fascist:
            # Fascists try to kill liberals
            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]
            if known_liberals:
                return choice(known_liberals)

        elif self.player.is_communist:
            # Communists try to kill fascists first, then liberals
            known_fascists = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "fascist"
            ]
            if known_fascists:
                return choice(known_fascists)

            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]
            if known_liberals:
                return choice(known_liberals)

        # Default to random
        return choice(eligible_players)

    def choose_player_to_inspect(self, eligible_players):
        """Choose a player to investigate"""
        # Always prefer uninspected players
        uninspected = [
            p for p in eligible_players if p.id not in self.player.inspected_players
        ]
        if uninspected:
            return choice(uninspected)

        # If all have been inspected, just pick randomly
        return choice(eligible_players)

    def choose_next_president(self, eligible_players):
        """Choose the next president for special election"""
        # Similar to chancellor nomination logic
        if self.player.is_fascist or self.player.is_hitler:
            # Prefer fascists/Hitler
            fascists = [p for p in eligible_players if p.is_fascist or p.is_hitler]
            if fascists:
                return choice(fascists)

        elif self.player.is_liberal:
            # Prefer known liberals
            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]
            if known_liberals:
                return choice(known_liberals)

        elif self.player.is_communist:
            # Prefer known communists
            if (
                hasattr(self.player, "known_communists")
                and self.player.known_communists
            ):
                known_communist_players = [
                    p for p in eligible_players if p.id in self.player.known_communists
                ]
                if known_communist_players:
                    return choice(known_communist_players)

        # Default to random
        return choice(eligible_players)

    def choose_player_to_radicalize(self, eligible_players):
        """Choose a player to convert to communist"""
        if self.player.is_communist:
            # Prefer fascists to convert (weaken fascists)
            known_fascists = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "fascist"
                and not p.is_hitler
            ]  # Cannot convert Hitler
            if known_fascists:
                return choice(known_fascists)

            # Then try liberals
            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]
            if known_liberals:
                return choice(known_liberals)

        # If not communist or no known targets, pick randomly
        return choice(eligible_players)

    # Emergency powers methods
    def propaganda_decision(self, policy):
        """Decide whether to discard the top policy"""
        # Fascists discard liberal policies
        if (
            self.player.is_fascist or self.player.is_hitler
        ) and policy.type == "liberal":
            return True

        # Liberals discard fascist policies
        if self.player.is_liberal and policy.type == "fascist":
            return True

        # Communists discard fascist policies, and sometimes liberal
        if self.player.is_communist:
            if policy.type == "fascist":
                return True
            if policy.type == "liberal":
                return random() <= 0.5  # 50% chance to discard liberal

        # Everyone keeps emergency power cards
        if policy.type in ["article48", "enablingact"]:
            return False

        # Keep own party's policies
        if self.player.is_fascist and policy.type == "fascist":
            return False
        if self.player.is_liberal and policy.type == "liberal":
            return False
        if self.player.is_communist and policy.type == "communist":
            return False

        # Default: 20% chance to discard
        return random() <= 0.2

    def choose_revealer(self, eligible_players):
        """Choose player to reveal party membership to (Impeachment)"""
        if self.player.is_fascist or self.player.is_hitler:
            # Reveal to a fellow fascist if possible
            fascists = [p for p in eligible_players if p.is_fascist]
            if fascists:
                return choice(fascists)

        elif self.player.is_liberal:
            # Reveal to a known liberal if possible
            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]
            if known_liberals:
                return choice(known_liberals)

        elif self.player.is_communist:
            # Reveal to a fellow communist if possible
            if (
                hasattr(self.player, "known_communists")
                and self.player.known_communists
            ):
                communists = [
                    p for p in eligible_players if p.id in self.player.known_communists
                ]
                if communists:
                    return choice(communists)

        return choice(eligible_players)  # Default: random choice

    def choose_player_to_mark(self, eligible_players):
        """Choose player to mark for execution (Marked for Execution)"""
        # Very similar to regular execution logic but might be more strategic
        # since the execution is delayed

        if self.player.is_liberal:
            # Try to mark a known fascist, prioritizing Hitler if known
            known_hitler = next(
                (
                    p
                    for p in eligible_players
                    if p.id in self.player.inspected_players
                    and self.player.inspected_players[p.id] == "fascist"
                    and p.is_hitler
                ),
                None,
            )
            if known_hitler:
                return known_hitler

            known_fascists = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "fascist"
            ]
            if known_fascists:
                return choice(known_fascists)

        elif self.player.is_fascist or self.player.is_hitler:
            # Mark a liberal or communist
            non_fascists = [p for p in eligible_players if not p.is_fascist]
            if non_fascists:
                return choice(non_fascists)

        elif self.player.is_communist:
            # Mark a fascist, then a liberal
            known_fascists = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "fascist"
            ]
            if known_fascists:
                return choice(known_fascists)

            known_liberals = [
                p
                for p in eligible_players
                if p.id in self.player.inspected_players
                and self.player.inspected_players[p.id] == "liberal"
            ]
            if known_liberals:
                return choice(known_liberals)

        return choice(eligible_players)  # Default: random choice

    def pardon_player(self):
        """Decide whether to pardon the marked player"""
        # Check if there's a marked player
        if (
            not hasattr(self.player.state, "marked_for_execution")
            or not self.player.state.marked_for_execution
        ):
            return False  # No one to pardon

        marked_player = self.player.state.marked_for_execution

        # Fascist president will ALWAYS pardon Hitler
        if (
            self.player.is_fascist or self.player.is_hitler
        ) and marked_player.is_hitler:
            return True

        # Fascist president will likely pardon fascists
        if (
            self.player.is_fascist or self.player.is_hitler
        ) and marked_player.is_fascist:
            return random() <= 0.9  # 90% chance to pardon

        # Liberal president will pardon known liberals
        if self.player.is_liberal and marked_player.id in self.player.inspected_players:
            if self.player.inspected_players[marked_player.id] == "liberal":
                return True

        # Communist president will pardon communists
        if self.player.is_communist and hasattr(self.player, "known_communists"):
            if marked_player.id in self.player.known_communists:
                return True

        # By default, random decision with bias toward not pardoning
        return random() <= 0.2  # 20% chance to pardon unknown players

    def social_democratic_removal_choice(self):
        """Choose policy track to remove from (Social Democratic)"""
        # Fascists remove from liberal track
        if self.player.is_fascist or self.player.is_hitler:
            return "liberal"

        # Liberals remove from fascist track
        if self.player.is_liberal:
            return "fascist"

        # Communists remove from fascist track more often than liberal
        if self.player.is_communist:
            if random() <= 0.7:
                return "fascist"
            else:
                return "liberal"

        # Default
        if random() <= 0.5:
            return "fascist"
        else:
            return "liberal"

    def choose_player_to_bug(self, eligible_players):
        """Choose a player to bug (view party membership)"""
        # Same logic as inspect - prioritize uninspected players
        return self.choose_player_to_inspect(eligible_players)

    def chancellor_veto_proposal(self, policies):
        """Decide whether to propose a veto as chancellor"""
        # Use similar logic to president veto decision
        return self.veto(policies)

    def vote_of_no_confidence(self):
        """Decide whether to enact the discarded policy"""
        if (
            not hasattr(self.player.state, "last_discarded")
            or not self.player.state.last_discarded
        ):
            return False

        policy = self.player.state.last_discarded

        # Fascists enact fascist policies
        if (
            self.player.is_fascist or self.player.is_hitler
        ) and policy.type == "fascist":
            return True

        # Liberals enact liberal policies
        if self.player.is_liberal and policy.type == "liberal":
            return True

        # Communists enact communist policies
        if self.player.is_communist and policy.type == "communist":
            return True

        # Default: 20% chance
        return random() <= 0.2
