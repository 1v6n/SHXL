"""Módulo del registro de poderes del juego Secret Hitler XL.

Este módulo contiene la clase PowerRegistry que gestiona todos los poderes
disponibles en el juego, incluyendo poderes fascistas, comunistas y de emergencia.
"""

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
    """Registro de todos los poderes disponibles en el juego.

    Esta clase proporciona métodos estáticos para obtener instancias de poderes,
    determinar sus propietarios y seleccionar poderes de emergencia aleatorios.
    """

    @staticmethod
    def get_power(power_name, game):
        """Obtiene un poder por su nombre.

        Args:
            power_name (str): Nombre del poder.
            game: Instancia del juego.

        Returns:
            Power: El objeto del poder.

        Raises:
            ValueError: Si el nombre del poder no es reconocido.
        """
        power_map = {
            "investigate_loyalty": InvestigateLoyalty,
            "special_election": SpecialElection,
            "policy_peek": PolicyPeek,
            "execution": Execution,
            "confession": Confession,
            "bugging": Bugging,
            "five_year_plan": FiveYearPlan,
            "congress": Congress,
            "radicalization": Radicalization,
            "propaganda": PresidentialPropaganda,
            "impeachment": PresidentialImpeachment,
            "marked_for_execution": PresidentialMarkedForExecution,
            "policy_peek_emergency": PresidentialPolicyPeek,
            "execution_emergency": PresidentialExecution,
            "pardon": PresidentialPardon,
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
        """Obtiene el propietario de un poder.

        Args:
            power_name (str): Nombre del poder.

        Returns:
            PowerOwner: El propietario del poder (PRESIDENT o CHANCELLOR).
        """
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

        return PowerOwner.PRESIDENT

    @staticmethod
    def get_article48_power():
        """Obtiene un poder aleatorio del Artículo 48 (poderes de emergencia del Presidente).

        Returns:
            str: Nombre del poder.
        """
        article48_powers = [
            "propaganda",
            "impeachment",
            "marked_for_execution",
            "policy_peek_emergency",
            "execution_emergency",
            "pardon",
        ]

        return choice(article48_powers)

    @staticmethod
    def get_enabling_act_power():
        """Obtiene un poder aleatorio de la Ley Habilitante (poderes de emergencia del Canciller).

        Returns:
            str: Nombre del poder.
        """
        enabling_act_powers = [
            "chancellor_propaganda",
            "chancellor_impeachment",
            "chancellor_marked_for_execution",
            "chancellor_policy_peek",
            "chancellor_execution",
            "vote_of_no_confidence",
        ]

        return choice(enabling_act_powers)
