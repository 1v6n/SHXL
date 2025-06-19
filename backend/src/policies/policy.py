"""Módulo de políticas del juego Secret Hitler XL.

Este módulo define las diferentes clases de políticas que pueden ser
promulgadas durante el juego, incluyendo políticas estándar y anti-políticas.
"""


class Policy:
    """Clase base para todos los tipos de políticas.
    Representa una política genérica con un tipo específico.
    """

    def __init__(self, policy_type):
        """Inicializa una política con el tipo especificado.

        Args:
            policy_type (str): El tipo de política.
        """
        self.type = policy_type

    def __repr__(self):
        """Devuelve una representación en cadena de la política.

        Returns:
            str: El tipo de política con la primera letra en mayúscula.
        """
        return self.type.title()


class Fascist(Policy):
    """Política fascista.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una política fascista."""
        super(Fascist, self).__init__("fascist")


class Liberal(Policy):
    """Política liberal.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una política liberal."""
        super(Liberal, self).__init__("liberal")


class Communist(Policy):
    """Política comunista.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una política comunista."""
        super(Communist, self).__init__("communist")


class AntiFascist(Policy):
    """Anti-política que elimina una política fascista.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una anti-política fascista."""
        super(AntiFascist, self).__init__("antifascist")


class AntiCommunist(Policy):
    """Anti-política que elimina una política comunista.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una anti-política comunista."""
        super(AntiCommunist, self).__init__("anticommunist")


class SocialDemocratic(Policy):
    """Anti-política que elimina una política fascista o comunista.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una política socialdemócrata."""
        super(SocialDemocratic, self).__init__("socialdemocratic")


class Article48(Policy):
    """Política de poder de emergencia para el Presidente.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una política de emergencia Article 48."""
        super(Article48, self).__init__("article48")


class EnablingAct(Policy):
    """Política de poder de emergencia para el Canciller.

    Hereda de:
        Policy: Clase base para todos los tipos de políticas.
    """

    def __init__(self):
        """Inicializa una política de emergencia Enabling Act."""
        super(EnablingAct, self).__init__("enablingact")
