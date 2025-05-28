from random import shuffle

from src.roles.role import Communist, Fascist, Hitler, Liberal


class RoleFactory:
    """Factory class to generate roles based on player count and game configuration.

    This class provides static methods to create role distributions for Secret Hitler XL,
    dynamically adjusting the contents based on number of players and optional configurations.
    """

    @staticmethod
    def get_role_counts(player_count, with_communists=True):
        """Get the number of each role type based on player count.

        Args:
            player_count (int): Number of players in the game.
            with_communists (bool): Whether to include communist roles.

        Returns:
            dict: Dictionary with role counts for each type.
        """
        # Role distribution according to the handbook
        role_distribution = {
            # With communists: (liberals, fascists, communists)
            6: {"with_communists": (3, 1, 1), "without_communists": (4, 1, 0)},
            7: {"with_communists": (4, 1, 1), "without_communists": (4, 2, 0)},
            8: {"with_communists": (4, 2, 1), "without_communists": (5, 2, 0)},
            9: {"with_communists": (4, 2, 2), "without_communists": (5, 3, 0)},
            10: {"with_communists": (5, 2, 2), "without_communists": (6, 3, 0)},
            11: {"with_communists": (5, 3, 2), "without_communists": (6, 4, 0)},
            12: {"with_communists": (6, 3, 2), "without_communists": (7, 4, 0)},
            13: {"with_communists": (6, 3, 3), "without_communists": (7, 5, 0)},
            14: {"with_communists": (7, 3, 3), "without_communists": (8, 5, 0)},
            15: {"with_communists": (7, 4, 3), "without_communists": (8, 6, 0)},
            16: {"with_communists": (7, 4, 4), "without_communists": (9, 6, 0)},
        }
        # Ensure player count is within bounds
        player_count = max(6, min(16, player_count))

        # Get the right distribution
        key = "with_communists" if with_communists else "without_communists"
        liberals, fascists, communists = role_distribution[player_count][key]

        return {
            "liberal": liberals,
            "fascist": fascists,
            "communist": communists,
            "hitler": 1,  # Always one Hitler
        }

    @staticmethod
    def create_roles(player_count, with_communists=True):
        """Create a list of roles based on player count.

        Args:
            player_count (int): Number of players in the game.
            with_communists (bool): Whether to include communist roles.

        Returns:
            list: A shuffled list of Role instances distributed according to game rules.
        """
        role_counts = RoleFactory.get_role_counts(player_count, with_communists)

        roles = []
        roles.extend([Liberal() for _ in range(role_counts["liberal"])])
        roles.extend([Fascist() for _ in range(role_counts["fascist"])])
        roles.append(Hitler())

        if with_communists:
            roles.extend([Communist() for _ in range(role_counts["communist"])])

        # Shuffle the roles
        shuffle(roles)

        return roles
