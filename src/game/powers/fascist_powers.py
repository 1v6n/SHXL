from src.game.powers.abstract_power import Power

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
