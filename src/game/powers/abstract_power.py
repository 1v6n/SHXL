from abc import ABC, abstractmethod
from enum import Enum, auto


class PowerOwner(Enum):
    """Types of power owners"""

    PRESIDENT = auto()
    CHANCELLOR = auto()


class Power(ABC):
    """Base class for all powers"""

    def __init__(self, game):
        self.game = game

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the power"""

    @staticmethod
    def get_owner():
        """Get the owner of this power"""
        return PowerOwner.PRESIDENT  # Default is president


# Fascist Powers


class InvestigateLoyalty(Power):
    def execute(self, target_player):
        """
        Investigates a player's party membership

        Args:
            target_player: The player to investigate

        Returns:
            str: The party membership of the target player
        """
        # Mark the player as investigated
        self.game.state.investigated_players.append(target_player)

        # Return the player's party membership
        return target_player.role.party_membership


class SpecialElection(Power):
    def execute(self, next_president):
        """
        Sets the next president for a special election

        Args:
            next_president: The player to be the next president

        Returns:
            player: The player selected as next president
        """
        # Store the current president index for returning after the special election
        self.game.state.special_election_return_index = self.game.state.president.id

        # Set the next president directly
        self.game.state.special_election = True
        self.game.state.president_candidate = next_president

        return next_president


class PolicyPeek(Power):
    def execute(self):
        """
        Views the top 3 policies in the draw pile

        Returns:
            list: The top 3 policies
        """
        # Get the top 3 policies without drawing them
        top_policies = self.game.state.board.policies[:3]

        return top_policies


class Execution(Power):
    def execute(self, target_player):
        """
        Executes a player

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


# Communist Powers


class Confession(Power):
    def execute(self):
        """
        President reveals their party membership

        Returns:
            str: The president's party membership
        """
        president = self.game.state.president
        self.game.state.revealed_affiliations[president.id] = (
            president.role.party_membership
        )

        return president.role.party_membership


class Bugging(Power):
    def execute(self, target_player):
        """
        Communists view another player's party membership

        Args:
            target_player: The player to investigate

        Returns:
            str: The party membership of the target player
        """
        # Only communists will see this information
        for player in self.game.state.players:
            if player.role.party_membership == "communist":
                if not hasattr(player, "known_affiliations"):
                    player.known_affiliations = {}
                player.known_affiliations[target_player.id] = (
                    target_player.role.party_membership
                )

        return target_player


class FiveYearPlan(Power):
    def execute(self):
        """
        Add 2 communist and 1 liberal policy to the deck

        Returns:
            bool: True if successful
        """
        from src.policies.policy import Communist, Liberal

        # Create the policies
        new_policies = [Communist(), Communist(), Liberal()]

        # Add them to the draw pile
        self.game.state.board.policies = new_policies + self.game.state.board.policies

        return True


class Congress(Power):
    def execute(self):
        """
        Communists learn who the original communists are

        Returns:
            dict: Dictionary of player IDs mapped to whether they are communist
        """
        # Get all original communists
        original_communists = [
            player.id
            for player in self.game.state.players
            if player.role.party_membership == "communist"
        ]

        # Share this information with all communists
        for player in self.game.state.players:
            if player.role.party_membership == "communist":
                player.known_communists = original_communists

        return original_communists


class Radicalization(Power):
    def execute(self, target_player):
        """
        Convert a player to communist

        Args:
            target_player: The player to convert

        Returns:
            player: The converted player or None if conversion failed
        """
        # Cannot convert Hitler or Capitalist
        if target_player.is_hitler:
            return None

        # Convert player to communist
        from src.roles.role import Communist

        target_player.role = Communist()

        # # Update communist knowledge based on player count
        # player_count = len(self.game.state.players)

        # # If less than 11 players, communists know each other
        # if player_count < 11:
        #     # Update the new communist's knowledge
        #     communist_players = [
        #         p
        #         for p in self.game.state.players
        #         if p.role.party_membership == "communist"
        #     ]

        #     for communist in communist_players:
        #         if not hasattr(communist, "known_communists"):
        #             communist.known_communists = []

        #         # Add all other communists to their knowledge
        #         for other in communist_players:
        #             if (
        #                 other.id != communist.id
        #                 and other.id not in communist.known_communists
        #             ):
        #                 communist.known_communists.append(other.id)

        # TODO if result is secret, should this be None?
        return target_player


class Propaganda(Power):
    def execute(self):
        """
        View the top card and optionally discard it

        Returns:
            policy: The viewed policy
        """
        if not self.game.state.board.policies:
            return None

        policy = self.game.state.board.policies[0]
        executor = self.game.state.president
        discard = executor.propaganda_decision(policy)

        if discard:
            self.game.state.board.policies.pop(0)
            self.game.state.board.discard(policy)

        return policy


class Impeachment(Power):
    def execute(self, target_player, revealer_player):
        """
        Chancellor reveals party to someone else

        Args:
            target_player: Player who must reveal their party
            revealer_player: Player who gets to see the party

        Returns:
            bool: True if successful
        """
        if not hasattr(revealer_player, "known_affiliations"):
            revealer_player.known_affiliations = {}

        revealer_player.known_affiliations[target_player.id] = (
            target_player.role.party_membership
        )

        return True
