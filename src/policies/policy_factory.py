from random import shuffle

from src.policies.policy import (
    AntiCommunist,
    AntiFascist,
    Article48,
    Communist,
    EnablingAct,
    Fascist,
    Liberal,
    SocialDemocratic,
)


class PolicyFactory:
    """Factory class to generate a deck of policy cards based on game settings.

    This class provides a static method to create a policy deck for Secret Hitler XL,
    dynamically adjusting the contents based on number of players and optional configurations.
    """

    @staticmethod
    def create_policy_deck(
        player_count,
        with_communists=True,
        with_anti_policies=False,
        with_emergency_powers=False,
    ):
        """Creates a policy deck based on game configuration.

        Args:
            player_count (int): Number of players in the game.
            with_communists (bool): Whether communist policies should be included.
            with_anti_policies (bool): Whether anti-policies should be included (requires communists).
            with_emergency_powers (bool): Whether emergency powers should be included for games with more than 10 players.

        Returns:
            list: A shuffled list of Policy instances, including liberal, fascist, communist,
                  anti-policies, and emergency powers depending on the settings.
        """
        if player_count < 8:
            liberal_count = 5
            fascist_count = 10
            communist_count = 8 if with_communists else 0
        else:
            liberal_count = 6
            fascist_count = 9
            communist_count = 8 if with_communists else 0

        policies = []
        policies.extend([Liberal() for _ in range(liberal_count)])
        policies.extend([Fascist() for _ in range(fascist_count)])

        if with_communists:
            policies.extend([Communist() for _ in range(communist_count)])

            if with_anti_policies:
                for i, policy in enumerate(policies):
                    if policy.type == "fascist":
                        policies[i] = AntiCommunist()
                        break

                for i, policy in enumerate(policies):
                    if policy.type == "communist":
                        policies[i] = AntiFascist()
                        break

                for i, policy in enumerate(policies):
                    if policy.type == "liberal":
                        policies[i] = SocialDemocratic()
                        break

        if with_emergency_powers and player_count > 10:
            emergency_count = min(player_count - 10, 6)

            if with_communists and player_count > 13:
                emergency_count = min((player_count - 13) * 2, 6)

            article48_count = emergency_count // 2 + (emergency_count % 2)
            enabling_acts_count = emergency_count // 2

            policies.extend([Article48() for _ in range(article48_count)])
            policies.extend([EnablingAct() for _ in range(enabling_acts_count)])

        shuffle(policies)
        return policies
