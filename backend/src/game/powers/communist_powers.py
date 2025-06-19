from src.game.powers.abstract_power import Power


class Confession(Power):
    """Poder de confesión comunista.

    Permite al Presidente revelar su afiliación partidaria a todos los jugadores,
    creando transparencia sobre su identidad política.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de confesión del Presidente.

        El Presidente revela públicamente su afiliación partidaria,
        haciendo que esta información esté disponible para todos los jugadores.

        Returns:
            str: La afiliación partidaria del Presidente.
        """
        president = self.game.state.president
        self.game.state.revealed_affiliations[president.id] = (
            president.role.party_membership
        )

        return president.role.party_membership


class Bugging(Power):
    """Poder de espionaje comunista.

    Permite a los comunistas investigar secretamente la afiliación partidaria
    de otro jugador, compartiendo esta información solo entre comunistas.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de espionaje.

        Los comunistas obtienen información sobre la afiliación partidaria
        de un jugador objetivo, manteniendo esta información en secreto
        entre los miembros del partido comunista.

        Args:
            target_player (Player): El jugador que será investigado.
                Puede pasarse como primer argumento en args o como kwarg.

        Returns:
            Player: El jugador investigado.
        """
        target_player = args[0] if args else kwargs.get("target_player")

        for player in self.game.state.players:
            if player.role.party_membership == "communist":
                if not hasattr(player, "known_affiliations"):
                    player.known_affiliations = {}
                player.known_affiliations[target_player.id] = (
                    target_player.role.party_membership
                )

        return target_player


class FiveYearPlan(Power):
    """Poder del Plan Quinquenal comunista.

    Permite manipular el mazo de políticas agregando nuevas cartas comunistas
    y liberales, alterando la distribución de políticas disponibles.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder del Plan Quinquenal.

        Agrega 2 políticas comunistas y 1 política liberal al mazo de cartas,
        mezclándolas con las políticas existentes para cambiar las probabilidades
        de promulgar diferentes tipos de políticas.

        Returns:
            bool: True si la operación fue exitosa.
        """
        from random import shuffle

        from src.policies.policy import Communist, Liberal

        new_policies = [Communist(), Communist(), Liberal()]

        self.game.state.board.policies = new_policies + self.game.state.board.policies
        shuffle(self.game.state.board.policies)

        return True


class Congress(Power):
    """Poder del Congreso comunista.

    Permite a los comunistas identificar a todos los miembros actuales del partido,
    útil para verificar si la radicalización de Hitler falló o para reorganizar estrategias.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder del Congreso.

        Revela a todos los comunistas quiénes son los miembros actuales del partido
        comunista, permitiendo verificar conversiones exitosas o fallidas.

        Returns:
            list: Lista de IDs de jugadores que son comunistas actualmente.
        """
        actual_communists = [
            player.id
            for player in self.game.state.players
            if player.role.party_membership == "communist"
        ]

        for player in self.game.state.players:
            if player.role.party_membership == "communist":
                player.known_communists = actual_communists

        return actual_communists


class Radicalization(Power):
    """Poder de radicalización comunista.

    Permite convertir a un jugador al comunismo, cambiando su afiliación
    partidaria y estrategia política, excepto en casos especiales como Hitler.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de radicalización.

        Convierte a un jugador objetivo al comunismo, cambiando su rol
        y estrategia política. Hitler y algunos otros roles especiales
        no pueden ser convertidos.

        Args:
            target_player (Player): El jugador que será convertido al comunismo.
                Puede pasarse como primer argumento en args o como kwarg.

        Returns:
            Player or None: El jugador convertido, o None si la conversión falló.
        """
        target_player = args[0] if args else kwargs.get("target_player")

        if target_player.is_hitler:
            return None

        from src.roles.role import Communist

        target_player.role = Communist()

        from src.players.strategies.communist_strategy import CommunistStrategy
        from src.players.strategies.fascist_strategy import FascistStrategy
        from src.players.strategies.liberal_strategy import LiberalStrategy

        if isinstance(target_player.strategy, (FascistStrategy, LiberalStrategy)):
            target_player.strategy = CommunistStrategy(target_player)

        return target_player


class Propaganda(Power):
    """Poder de propaganda comunista.

    Permite al ejecutor ver la carta superior del mazo y opcionalmente descartarla,
    proporcionando control sobre las políticas que se promulgarán a continuación.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de propaganda.

        Permite al Presidente ver la carta superior del mazo de políticas
        y decidir si la descarta o la mantiene, influyendo en las próximas
        decisiones políticas del juego.

        Returns:
            Policy or None: La política vista, o None si no hay políticas disponibles.
        """
        if not self.game.state.board.policies:
            return None

        policy = self.game.state.board.policies[0]
        executor = self.game.state.president
        discard = executor.propaganda_decision(policy)

        if discard:
            self.game.state.board.policies.pop(0)
            self.game.state.board.discard(policy)

        return policy


class Impeachment(Power):
    """Poder de acusación comunista.

    Obliga a un jugador a revelar su afiliación partidaria a otro jugador específico,
    creando dinámicas de información asimétrica y posibles alianzas o traiciones.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de acusación.

        Fuerza a un jugador objetivo a revelar su afiliación partidaria
        a un jugador específico elegido por quien ejecuta el poder.

        Args:
            target_player (Player): El jugador que debe revelar su afiliación.
                Puede pasarse como primer argumento en args o como kwarg.
            revealer_player (Player): El jugador que verá la afiliación.
                Puede pasarse como segundo argumento en args o como kwarg.

        Returns:
            bool: True si la operación fue exitosa.
        """
        if len(args) >= 2:
            target_player = args[0]
            revealer_player = args[1]
        else:
            target_player = args[0] if args else kwargs.get("target_player")
            revealer_player = kwargs.get("revealer_player")

        if not hasattr(revealer_player, "known_affiliations"):
            revealer_player.known_affiliations = {}

        revealer_player.known_affiliations[target_player.id] = (
            target_player.role.party_membership
        )

        return True
