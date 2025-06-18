from random import choice, random

from src.players.strategies.base_strategy import PlayerStrategy


class CommunistStrategy(PlayerStrategy):
    """Strategy for Communist players in Secret Hitler XL.

    Implements decision logic for all game actions a communist player may take.
    """

    def nominate_chancellor(self, eligible_players):
        """Selects a chancellor nominee.

        First prefers a known communist, then a non-fascist, otherwise random.

        Args:
            eligible_players (list[Player]): List of players eligible to be nominated.

        Returns:
            Player: The chosen chancellor nominee.
        """
        known_communists = [
            p for p in eligible_players if p.id in self.player.known_communists
        ]
        if known_communists:
            return choice(known_communists)

        known_fascists = [
            p
            for p in eligible_players
            if p.id in self.player.known_affiliations
            and self.player.known_affiliations[p.id] == "fascist"
        ]
        non_fascists = [p for p in eligible_players if p not in known_fascists]
        if non_fascists:
            return choice(non_fascists)
        return choice(eligible_players)

    def filter_policies(self, policies):
        """Chooses which two policies to keep and which to discard.

        Prefers communist policies, then liberal, then fascist.

        Args:
            policies (list[Policy]): The three drawn policies.

        Returns:
            tuple[list[Policy], Policy]: (The two kept policies, the discarded policy)
        """
        sorted_policies = sorted(
            policies,
            key=lambda p: (
                1 if p.type == "communist" else (0.5 if p.type == "liberal" else 0)
            ),
            reverse=True,
        )
        chosen = sorted_policies[:2]
        discarded = sorted_policies[2]
        return chosen, discarded

    def choose_policy(self, policies):
        """Selects a policy to enact and one to discard.

        Args:
            policies (list[Policy]): The two drawn policies.

        Returns:
            tuple[Policy, Policy]: (Chosen policy to enact, discarded policy)
        """
        sorted_policies = sorted(
            policies,
            key=lambda p: (
                1 if p.type == "communist" else (0.5 if p.type == "liberal" else 0)
            ),
            reverse=True,
        )
        chosen = sorted_policies[0]
        discarded = sorted_policies[1]
        return chosen, discarded

    def vote(self, president, chancellor):
        """Decides how to vote for a government.

        Args:
            president (Player): The nominated president.
            chancellor (Player): The nominated chancellor.

        Returns:
            bool: True for Ja (yes), False for Nein (no).
        """
        president_communist = president.id in self.player.known_communists
        chancellor_communist = chancellor.id in self.player.known_communists
        if president_communist or chancellor_communist:
            return True

        chancellor_fascist = (
            chancellor.id in self.player.known_affiliations
            and self.player.known_affiliations[chancellor.id] == "fascist"
        )
        if chancellor_fascist:
            return False

        if self.player.state.fascist_track >= 3:
            if chancellor.id not in self.player.known_affiliations:
                return random() <= 0.3

        communist_track = self.player.state.board.communist_track
        communist_track_size = self.player.state.board.communist_track_size
        if communist_track >= communist_track_size - 2:
            return random() <= 0.8

        return random() <= 0.6

    def veto(self, policies):
        """Determines whether to propose a veto.

        Args:
            policies (list[Policy]): Policies in hand.

        Returns:
            bool: True to propose veto, False otherwise.
        """
        communist_policies = [p for p in policies if p.type == "communist"]
        fascist_policies = [p for p in policies if p.type == "fascist"]
        return len(communist_policies) == 0 and len(fascist_policies) > 0

    def accept_veto(self, policies):
        """Determines whether to accept a veto as president.

        Args:
            policies (list[Policy]): Policies in hand.

        Returns:
            bool: True to accept, False to reject.
        """
        communist_policies = [p for p in policies if p.type == "communist"]
        fascist_policies = [p for p in policies if p.type == "fascist"]
        return not communist_policies and fascist_policies

    def choose_player_to_kill(self, eligible_players):
        """Selects a player to execute.

        Tries Hitler first if known, then fascists, then non-allies.

        Args:
            eligible_players (list[Player]): Candidates for execution.

        Returns:
            Player: Player chosen to be executed.
        """
        known_hitler = next(
            (
                p
                for p in eligible_players
                if p.id in self.player.known_affiliations
                and self.player.known_affiliations[p.id] == "fascist"
                and p.is_hitler
            ),
            None,
        )
        if known_hitler:
            return known_hitler

        known_fascists = [
            p
            for p in eligible_players
            if p.id in self.player.known_affiliations
            and self.player.known_affiliations[p.id] == "fascist"
        ]
        if known_fascists:
            return choice(known_fascists)

        # Here you could use tracked suspicious players logic.
        # For now, simply avoid known allies.
        known_friendly = [
            p
            for p in eligible_players
            if (p.id in self.player.known_communists)
            or (
                p.id in self.player.known_affiliations
                and self.player.known_affiliations[p.id] == "liberal"
            )
        ]
        non_friendly = [p for p in eligible_players if p not in known_friendly]
        if non_friendly:
            return choice(non_friendly)
        return choice(eligible_players)

    def choose_player_to_inspect(self, eligible_players):
        """Selects a player to inspect (bug).

        Prefers non-communists and those not previously inspected.

        Args:
            eligible_players (list[Player]): Players available to inspect.

        Returns:
            Player: Player to inspect.
        """
        known_communists = [
            p for p in eligible_players if p.id in self.player.known_communists
        ]
        non_communists = [p for p in eligible_players if p not in known_communists]
        uninspected = [
            p for p in non_communists if p.id not in self.player.known_affiliations
        ]
        if uninspected:
            return choice(uninspected)
        non_liberal = [
            p
            for p in non_communists
            if p.id not in self.player.known_affiliations
            or self.player.known_affiliations[p.id] != "liberal"
        ]
        if non_liberal:
            return choice(non_liberal)
        if non_communists:
            return choice(non_communists)
        return choice(eligible_players)

    def choose_next_president(self, eligible_players):
        """Selects the next president, preferring communists.

        Args:
            eligible_players (list[Player]): Players eligible to be president.

        Returns:
            Player: Chosen next president.
        """
        known_communists = [
            p for p in eligible_players if p.id in self.player.known_communists
        ]
        if known_communists:
            return choice(known_communists)
        non_fascists = [
            p
            for p in eligible_players
            if p.id not in self.player.known_affiliations
            or self.player.known_affiliations[p.id] != "fascist"
        ]
        if non_fascists:
            return choice(non_fascists)
        return choice(eligible_players)

    def choose_player_to_radicalize(self, eligible_players):
        """Selects a player to radicalize, preferring liberals, avoiding Hitler.

        Args:
            eligible_players (list[Player]): Players available to radicalize.

        Returns:
            Player: Chosen player to radicalize.
        """
        known_liberals = [
            p
            for p in eligible_players
            if p.id in self.player.known_affiliations
            and self.player.known_affiliations[p.id] == "liberal"
            and not p.is_hitler
        ]
        if known_liberals:
            return choice(known_liberals)
        known_communists = [
            p for p in eligible_players if p.id in self.player.known_communists
        ]
        known_fascists = [
            p
            for p in eligible_players
            if p.id in self.player.known_affiliations
            and self.player.known_affiliations[p.id] == "fascist"
        ]
        known_hitler = next(
            (
                p
                for p in eligible_players
                if p.id in self.player.known_affiliations and p.is_hitler
            ),
            None,
        )
        ineligible = known_communists + known_fascists
        if known_hitler:
            ineligible.append(known_hitler)
        eligible_non_communists = [p for p in eligible_players if p not in ineligible]
        if eligible_non_communists:
            return choice(eligible_non_communists)
        return choice(eligible_players)

    def choose_player_to_mark(self, eligible_players):
        """Selects a player to mark for execution.

        Args:
            eligible_players (list[Player]): Candidates for execution.

        Returns:
            Player: Chosen player to mark.
        """
        return self.choose_player_to_kill(eligible_players)

    def choose_player_to_bug(self, eligible_players):
        """Selects a player to bug (inspect party membership).

        Args:
            eligible_players (list[Player]): Candidates to bug.

        Returns:
            Player: Chosen player to bug.
        """
        return self.choose_player_to_inspect(eligible_players)

    def propaganda_decision(self, policy):
        """Decides whether to discard the top policy during a propaganda action.

        Args:
            policy (Policy): The policy at the top of the deck.

        Returns:
            bool: True to discard, False to keep.
        """
        if policy.type == "fascist":
            return True
        elif policy.type == "communist":
            return False
        elif policy.type == "liberal":
            return choice([True, False])
        return choice([True, False])

    def choose_revealer(self, eligible_players):
        """Selects a player to reveal party membership to (Impeachment).

        Args:
            eligible_players (list[Player]): Candidates for reveal.

        Returns:
            Player: Chosen player to reveal.
        """
        known_communists = [
            p for p in eligible_players if p.id in self.player.known_communists
        ]
        if known_communists:
            return choice(known_communists)
        non_fascists = [
            p
            for p in eligible_players
            if p.id not in self.player.known_affiliations
            or self.player.known_affiliations[p.id] != "fascist"
        ]
        if non_fascists:
            return choice(non_fascists)
        return choice(eligible_players)

    def pardon_player(self):
        """Decides whether to pardon a player marked for execution.

        Returns:
            bool: True to pardon, False otherwise.
        """
        if (
            not hasattr(self.player.state, "marked_for_execution")
            or not self.player.state.marked_for_execution
        ):
            return False
        marked_player = self.player.state.marked_for_execution

        # Always pardon fellow communists
        if marked_player.id in self.player.known_communists:
            return True

        # Check via inspected players attribute
        if (
            hasattr(self.player, "inspected_players")
            and marked_player.id in self.player.inspected_players
        ):
            if self.player.inspected_players[marked_player.id] == "communist":
                return True
            elif self.player.inspected_players[marked_player.id] == "fascist":
                return False
            elif self.player.inspected_players[marked_player.id] == "liberal":
                return choice([True, True, False])  # Bias toward pardoning

        # Check via known affiliations
        if (
            hasattr(self.player, "known_affiliations")
            and marked_player.id in self.player.known_affiliations
        ):
            if self.player.known_affiliations[marked_player.id] == "liberal":
                return choice([True, True, False])  # Bias toward pardoning
            elif self.player.known_affiliations[marked_player.id] == "fascist":
                return False

        # Don't pardon unknown players - too risky
        return False

    def chancellor_veto_proposal(self, policies):
        """Decides whether to propose a veto as chancellor.

        Args:
            policies (list[Policy]): Policies in hand.

        Returns:
            bool: True to propose veto, False otherwise.
        """
        communist_policies = [p for p in policies if p.type == "communist"]
        fascist_policies = [p for p in policies if p.type == "fascist"]
        return len(communist_policies) == 0 and len(fascist_policies) > 0

    def vote_of_no_confidence(self):
        """Decides whether to enact the discarded policy (Vote of No Confidence).

        Returns:
            bool: True to enact, False otherwise.
        """
        if (
            not hasattr(self.player.state, "last_discarded")
            or not self.player.state.last_discarded
        ):
            return False
        if self.player.state.last_discarded.type == "communist":
            return choice([True, False])  # Changed from True
        elif self.player.state.last_discarded.type == "liberal":
            return choice([True, False])
        elif self.player.state.last_discarded.type == "fascist":
            return choice([True, False])  # Changed from False
        return choice([True, False])

    def social_democratic_removal_choice(self):
        """Selects which policy track to remove from (Social Democratic power).

        Returns:
            str: Policy track to remove from ("fascist" or "liberal").
        """
        if self.player.state.fascist_track > 0:
            return "fascist"
        elif self.player.state.liberal_track > 0:
            return "liberal"
        else:
            return choice(["fascist", "liberal"])
