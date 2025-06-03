from src.game.powers.abstract_power import Power, PowerOwner


class EnablingActPower(Power):
    """Base class for Enabling Act powers (Chancellor's emergency powers)"""

    @staticmethod
    def get_owner():
        """Get the owner of this power"""
        return PowerOwner.CHANCELLOR


class ChancellorPropaganda(EnablingActPower):
    def execute(self):
        """
        Chancellor can view the top card and optionally discard it

        Returns:
            policy: The viewed policy
        """
        if not self.game.state.board.policies:
            return None

        policy = self.game.state.board.policies[0]
        discard = self.game.state.chancellor.propaganda_decision(policy)

        if discard:
            self.game.state.board.policies.pop(0)
            self.game.state.board.discard(policy)

        return policy


class ChancellorPolicyPeek(EnablingActPower):
    def execute(self):
        """
        Chancellor views the top 3 policies in the draw pile

        Returns:
            list: The top 3 policies
        """
        # Get the top 3 policies without drawing them
        top_policies = self.game.state.board.policies[:3]

        return top_policies


class ChancellorImpeachment(EnablingActPower):
    def execute(self, revealer_player=None):
        """
        Chancellor reveals their party to someone chosen by the president

        Args:
            revealer_player: Player who gets to see the party (chosen by president)

        Returns:
            bool: True if successful
        """
        # Chancellor is the one revealing their party
        target_player = self.game.state.chancellor

        # If revealer_player is not provided, president must choose
        if revealer_player is None:
            # Get eligible players (not president or chancellor)
            eligible_players = [
                p
                for p in self.game.state.active_players
                if p.id != self.game.state.president.id and p.id != target_player.id
            ]
            if not eligible_players:
                return False

            # President chooses who gets to see the chancellor's party
            revealer_player = self.game.state.president.choose_revealer(
                eligible_players
            )

        if not hasattr(revealer_player, "known_affiliations"):
            revealer_player.known_affiliations = {}

        revealer_player.known_affiliations[target_player.id] = (
            target_player.role.party_membership
        )

        return True


class ChancellorMarkedForExecution(EnablingActPower):
    def execute(self, target_player):
        """
        Chancellor marks a player for execution after 3 fascist policies

        Args:
            target_player: The player to mark

        Returns:
            player: The marked player
        """
        # Store the player and how the fascist tracker was when they were marked
        self.game.state.marked_for_execution = target_player
        self.game.state.marked_for_execution_tracker = (
            self.game.state.board.fascist_track
        )

        # Log that the player was marked for future execution
        self.game.logger.log(
            f"Player {target_player.id} ({target_player.name}) has been marked for execution by Chancellor {self.game.state.chancellor.name}."
        )
        self.game.logger.log(
            f"Current fascist track is {self.game.state.board.fascist_track}. They will be executed after 3 more fascist policies are enacted if not pardoned."
        )

        return target_player


class ChancellorExecution(EnablingActPower):
    def execute(self, target_player):
        """
        Chancellor executes a player

        Args:
            target_player: The player to execute

        Returns:
            player: The executed player
        """
        # Mark the player as dead
        target_player.is_dead = True

        # Remove from active players
        if target_player in self.game.state.active_players:
            self.game.state.active_players.remove(target_player)

        return target_player


class VoteOfNoConfidence(EnablingActPower):
    def execute(self):
        """
        Chancellor enacts the discarded policy (specific to Enabling Act)

        Returns:
            policy: The enacted policy or None
        """
        if not self.game.state.last_discarded:
            return None

        policy = self.game.state.last_discarded
        self.game.state.board.enact_policy(policy)

        return policy
