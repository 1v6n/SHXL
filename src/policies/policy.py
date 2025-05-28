class Policy(object):
    """Base class for all policy types."""

    def __init__(self, type):

        self.type = type

    def __repr__(self):

        return self.type.title()


class Fascist(Policy):
    """Fascist policy card.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes a fascist policy."""
        super(Fascist, self).__init__("fascist")


class Liberal(Policy):
    """Liberal policy card.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes a liberal policy."""
        super(Liberal, self).__init__("liberal")


class Communist(Policy):
    """Communist policy card.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes a communist policy."""
        super(Communist, self).__init__("communist")


class AntiFascist(Policy):
    """Anti-policy that removes a fascist policy.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes an anti-fascist policy."""
        super(AntiFascist, self).__init__("antifascist")


class AntiCommunist(Policy):
    """Anti-policy that removes a communist policy.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes an anti-communist policy."""
        super(AntiCommunist, self).__init__("anticommunist")


class SocialDemocratic(Policy):
    """Anti-policy that removes either a fascist or communist policy.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes a social-democratic policy."""
        super(SocialDemocratic, self).__init__("socialdemocratic")


class Article48(Policy):
    """Emergency power policy for the President.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes an Article 48 emergency policy."""
        super(Article48, self).__init__("article48")


class EnablingAct(Policy):
    """Emergency power policy for the Chancellor.

    Inherits from:
        Policy: Base class for all policy types.
    """

    def __init__(self):
        """Initializes an Enabling Act emergency policy."""
        super(EnablingAct, self).__init__("enablingact")
