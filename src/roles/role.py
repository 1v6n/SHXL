class Role(object):
    """Base class for all role types."""

    def __init__(self):
        self.party_membership = ""
        self.role = ""

    def __repr__(self):
        return self.role.title()


class Liberal(Role):
    """Liberal role card.

    Inherits from:
        Role: Base class for all role types.
    """

    def __init__(self):
        """Initializes a liberal role."""
        super(Liberal, self).__init__()
        self.party_membership = "liberal"
        self.role = "liberal"


class Fascist(Role):
    """Fascist role card.

    Inherits from:
        Role: Base class for all role types.
    """

    def __init__(self):
        """Initializes a fascist role."""
        super(Fascist, self).__init__()
        self.party_membership = "fascist"
        self.role = "fascist"


class Hitler(Role):
    """Hitler role card.

    Inherits from:
        Role: Base class for all role types.
    """

    def __init__(self):
        """Initializes a Hitler role."""
        super(Hitler, self).__init__()
        self.party_membership = "fascist"
        self.role = "hitler"


class Communist(Role):
    """Communist role card.

    Inherits from:
        Role: Base class for all role types.
    """

    def __init__(self):
        """Initializes a communist role."""
        super(Communist, self).__init__()
        self.party_membership = "communist"
        self.role = "communist"
