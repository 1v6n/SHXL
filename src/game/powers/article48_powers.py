from src.game.powers.abstract_power import Power, PowerOwner


class Article48Power(Power):
    """Base class for Article 48 powers (President's emergency powers)"""

    @staticmethod
    def get_owner():
        """Get the owner of this power"""
        return PowerOwner.PRESIDENT


class PresidentialPropaganda(Article48Power):
    def execute(self):
        """
        President can view the top card and optionally discard it

        Returns:
            policy: The viewed policy
        """
        if not self.game.state.board.policies:
            return None

        policy = self.game.state.board.policies[0]
        discard = self.game.state.president.propaganda_decision(policy)

        if discard:
            self.game.state.board.policies.pop(0)
            self.game.state.board.discard(policy)

        return policy


class PresidentialPolicyPeek(Article48Power):
    def execute(self):
        """
        President views the top 3 policies in the draw pile

        Returns:
            list: The top 3 policies
        """
        # Get the top 3 policies without drawing them
        top_policies = self.game.state.board.policies[:3]

        return top_policies


class PresidentialImpeachment(Article48Power):
    def execute(self, target_player, revealer_player=None):
        """
        Chancellor reveals party to someone chosen by the president

        Args:
            target_player: Player who must reveal their party (the chancellor)
            revealer_player: Player who gets to see the party (chosen by president)

        Returns:
            bool: True if successful
        """
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

            revealer_player = self.game.state.president.choose_revealer(
                eligible_players
            )

        if not hasattr(revealer_player, "known_affiliations"):
            revealer_player.known_affiliations = {}

        revealer_player.known_affiliations[target_player.id] = (
            target_player.role.party_membership
        )

        return True


class PresidentialMarkedForExecution(Article48Power):
    def execute(self, target_player):
        """
        President marks a player for execution after 3 fascist policies

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
            f"Player {target_player.id} ({target_player.name}) has been marked for execution."
        )
        self.game.logger.log(
            f"Current fascist track is {self.game.state.board.fascist_track}. They will be executed after 3 more fascist policies are enacted if not pardoned."
        )

        return target_player


class PresidentialExecution(Article48Power):
    def execute(self, target_player):
        """
        President executes a player

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


class PresidentialPardon(Article48Power):
    def execute(self):
        """
        President pardons a marked player

        Returns:
            player: The pardoned player or None (if there wasn't a marked player)
        """
        if not self.game.state.marked_for_execution:
            self.game.logger.log("No player is currently marked for execution.")
            return None

        pardoned = self.game.state.marked_for_execution
        self.game.logger.log(
            f"Player {pardoned.id} ({pardoned.name}) has been pardoned from execution."
        )

        # Clear the marked for execution
        self.game.state.marked_for_execution = None
        self.game.state.marked_for_execution_tracker = None

        return pardoned
