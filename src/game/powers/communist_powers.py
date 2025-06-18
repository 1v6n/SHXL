from src.game.powers.abstract_power import Power

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
        from random import shuffle

        from src.policies.policy import Communist, Liberal

        # Create the policies
        new_policies = [Communist(), Communist(), Liberal()]

        # Add them to the draw pile
        self.game.state.board.policies = new_policies + self.game.state.board.policies
        shuffle(self.game.state.board.policies)

        return True


class Congress(Power):
    def execute(self):
        """
        Communists learn who the communists are right now (can be used to check if radicalization failed on Hitler)

        Returns:
            dict: Dictionary of player IDs mapped to whether they are communist
        """
        # Get all actual communists
        actual_communists = [
            player.id
            for player in self.game.state.players
            if player.role.party_membership == "communist"
        ]

        # Share this information with all communists
        for player in self.game.state.players:
            if player.role.party_membership == "communist":
                player.known_communists = actual_communists

        return actual_communists


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

        # Change strategy to communist if player had fascist or liberal strategy
        from src.players.strategies.communist_strategy import CommunistStrategy
        from src.players.strategies.fascist_strategy import FascistStrategy
        from src.players.strategies.liberal_strategy import LiberalStrategy

        if isinstance(target_player.strategy, (FascistStrategy, LiberalStrategy)):
            target_player.strategy = CommunistStrategy(target_player)

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
