"""Fábrica de políticas para Secret Hitler XL.

Este módulo proporciona funcionalidades para generar mazos de cartas de políticas
basados en la configuración del juego y número de jugadores.
"""

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
    """Fábrica para generar un mazo de cartas de políticas basado en la configuración del juego.

    Esta clase proporciona un método estático para crear un mazo de políticas para Secret Hitler XL,
    ajustando dinámicamente el contenido basado en el número de jugadores y configuraciones opcionales.
    """

    @staticmethod
    def create_policy_deck(
        player_count,
        with_communists=True,
        with_anti_policies=False,
        with_emergency_powers=False,
    ):
        """Crea un mazo de políticas basado en la configuración del juego.

        Args:
            player_count (int): Número de jugadores en el juego.
            with_communists (bool): Si se deben incluir políticas comunistas.
            with_anti_policies (bool): Si se deben incluir anti-políticas (requiere comunistas).
            with_emergency_powers (bool): Si se deben incluir poderes de emergencia para juegos
                con más de 10 jugadores.

        Returns:
            list: Una lista mezclada de instancias de Policy, incluyendo liberales, fascistas,
                comunistas, anti-políticas y poderes de emergencia según la configuración.
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
