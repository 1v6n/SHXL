from random import choice

from src.game.powers.abstract_power import (
    Bugging,
    Confession,
    Congress,
    Execution,
    FiveYearPlan,
    InvestigateLoyalty,
    PolicyPeek,
    PowerOwner,
    Radicalization,
    SpecialElection,
)
from src.game.powers.article48_powers import (
    PresidentialExecution,
    PresidentialImpeachment,
    PresidentialMarkedForExecution,
    PresidentialPardon,
    PresidentialPolicyPeek,
    PresidentialPropaganda,
)
from src.game.powers.enabling_act_powers import (
    ChancellorExecution,
    ChancellorImpeachment,
    ChancellorMarkedForExecution,
    ChancellorPolicyPeek,
    ChancellorPropaganda,
    VoteOfNoConfidence,
)


class PowerRegistry:
    """Registry of all powers"""

    @staticmethod
    def get_power(power_name, game):
        """
        Get a power by name

        Args:
            power_name: Name of the power
            game: The game instance

        Returns:
            Power: The power object
        """
        power_map = {
            # Fascist powers
            "investigate_loyalty": InvestigateLoyalty,
            "special_election": SpecialElection,
            "policy_peek": PolicyPeek,
            "execution": Execution,
            # Communist powers
            "confession": Confession,
            "bugging": Bugging,
            "five_year_plan": FiveYearPlan,
            "congress": Congress,
            "radicalization": Radicalization,
            # Article 48 powers (President)
            "propaganda": PresidentialPropaganda,
            "impeachment": PresidentialImpeachment,
            "marked_for_execution": PresidentialMarkedForExecution,
            "policy_peek_emergency": PresidentialPolicyPeek,
            "execution_emergency": PresidentialExecution,
            "pardon": PresidentialPardon,
            # Enabling Act powers (Chancellor)
            "chancellor_propaganda": ChancellorPropaganda,
            "chancellor_impeachment": ChancellorImpeachment,
            "chancellor_marked_for_execution": ChancellorMarkedForExecution,
            "chancellor_policy_peek": ChancellorPolicyPeek,
            "chancellor_execution": ChancellorExecution,
            "vote_of_no_confidence": VoteOfNoConfidence,
        }

        if power_name not in power_map:
            raise ValueError(f"Unknown power: {power_name}")

        return power_map[power_name](game)

    @staticmethod
    def get_owner(power_name):
        """
        Get the owner of a power

        Args:
            power_name: Name of the power

        Returns:
            PowerOwner: The owner of the power (PRESIDENT or CHANCELLOR)
        """
        # Chancellor powers
        chancellor_powers = {
            "chancellor_propaganda",
            "chancellor_impeachment",
            "chancellor_marked_for_execution",
            "chancellor_policy_peek",
            "chancellor_execution",
            "vote_of_no_confidence",
        }

        if power_name in chancellor_powers:
            return PowerOwner.CHANCELLOR

        # All other powers belong to the president
        return PowerOwner.PRESIDENT

    @staticmethod
    def get_article48_power():
        """
        Get a random Article 48 power (President's emergency powers)

        Returns:
            str: Power name
        """

        article48_powers = [
            "propaganda",
            "impeachment",
            "marked_for_execution",
            "policy_peek_emergency",
            "execution_emergency",
            "pardon",
        ]

        # TODO this is for testing purposes, should be randomized in the future

        return article48_powers[3]

    @staticmethod
    def get_enabling_act_power():
        """
        Get a random Enabling Act power (Chancellor's emergency powers)

        Returns:
            str: Power name
        """

        enabling_act_powers = [
            "chancellor_propaganda",
            "chancellor_impeachment",
            "chancellor_marked_for_execution",
            "chancellor_policy_peek",
            "chancellor_execution",
            "vote_of_no_confidence",
        ]

        # TODO this is for testing purposes, should be randomized in the future

        return enabling_act_powers[5]
