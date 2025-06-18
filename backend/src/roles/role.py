"""Módulo de roles del juego Secret Hitler XL.

Este módulo define las diferentes clases de roles que pueden ser asignados
a los jugadores durante el juego.
"""


class Role:
    """Clase base para todos los tipos de roles.

    Define la estructura básica de un rol con membresía partidaria y tipo de rol.
    """

    def __init__(self):
        """Inicializa un rol con valores por defecto."""
        self.party_membership = ""
        self.role = ""

    def __repr__(self):
        """Devuelve una representación en cadena del rol.

        Returns:
            str: El tipo de rol con la primera letra en mayúscula.
        """
        return self.role.title()


class Liberal(Role):
    """Rol de jugador liberal.

    Hereda de:
        Role: Clase base para todos los tipos de roles.
    """

    def __init__(self):
        """Inicializa un rol liberal."""
        super(Liberal, self).__init__()
        self.party_membership = "liberal"
        self.role = "liberal"


class Fascist(Role):
    """Rol de jugador fascista.

    Hereda de:
        Role: Clase base para todos los tipos de roles.
    """

    def __init__(self):
        """Inicializa un rol fascista."""
        super(Fascist, self).__init__()
        self.party_membership = "fascist"
        self.role = "fascist"


class Hitler(Role):
    """Rol de Hitler.

    Hereda de:
        Role: Clase base para todos los tipos de roles.
    """

    def __init__(self):
        """Inicializa un rol de Hitler."""
        super(Hitler, self).__init__()
        self.party_membership = "fascist"
        self.role = "hitler"


class Communist(Role):
    """Rol de jugador comunista.

    Hereda de:
        Role: Clase base para todos los tipos de roles.
    """

    def __init__(self):
        """Inicializa un rol comunista."""
        super(Communist, self).__init__()
        self.party_membership = "communist"
        self.role = "communist"
