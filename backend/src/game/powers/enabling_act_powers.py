from src.game.powers.abstract_power import Power, PowerOwner


class EnablingActPower(Power):
    """Clase base para los poderes del Acta Habilitante (poderes de emergencia del Canciller).

    Esta clase define la estructura común para todos los poderes especiales que puede
    ejercer el Canciller cuando se activa el Acta Habilitante en el juego.
    """

    @staticmethod
    def get_owner():
        """Obtiene el propietario de este poder.

        Returns:
            PowerOwner: El propietario del poder (CHANCELLOR).
        """
        return PowerOwner.CHANCELLOR


class ChancellorPropaganda(EnablingActPower):
    """Poder de propaganda del Canciller.

    Permite al Canciller ver la carta superior del mazo y opcionalmente descartarla
    para influir en las políticas que se van a promulgar.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de propaganda del Canciller.

        El Canciller puede ver la carta superior del mazo de políticas y decidir
        si la descarta o la mantiene en el mazo.

        Returns:
            Policy or None: La política vista, o None si no hay políticas disponibles.
        """
        if not self.game.state.board.policies:
            return None

        policy = self.game.state.board.policies[0]
        discard = self.game.state.chancellor.propaganda_decision(policy)

        if discard:
            self.game.state.board.policies.pop(0)
            self.game.state.board.discard(policy)

        return policy


class ChancellorPolicyPeek(EnablingActPower):
    """Poder de inspección de políticas del Canciller.

    Permite al Canciller ver las tres cartas superiores del mazo de políticas
    sin extraerlas, proporcionando información estratégica sobre las próximas políticas.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de inspección de políticas.

        Permite al Canciller examinar las tres cartas superiores del mazo
        de políticas para obtener información estratégica.

        Returns:
            list: Lista con las tres políticas superiores del mazo.
        """
        top_policies = self.game.state.board.policies[:3]
        return top_policies


class ChancellorImpeachment(EnablingActPower):
    """Poder de acusación del Canciller.

    Permite al Canciller revelar su afiliación partidaria a un jugador
    elegido por el Presidente, creando dinámicas de confianza y desconfianza.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de acusación del Canciller.

        El Canciller revela su afiliación partidaria a un jugador específico
        que es elegido por el Presidente.

        Args:
            revealer_player (Player, optional): Jugador que podrá ver la afiliación
                del Canciller. Si no se proporciona, el Presidente debe elegir uno.
                Puede pasarse a través de kwargs.

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        revealer_player = kwargs.get("revealer_player", None)
        target_player = self.game.state.chancellor

        if revealer_player is None:
            eligible_players = [
                p
                for p in self.game.state.active_players
                if p.id != self.game.state.president.id and p.id != target_player.id
            ]
            if not eligible_players:
                return False

            revealer_player = self.game.state.president.choose_revealer(
                eligible_players
            )

        if not hasattr(revealer_player, "known_affiliations"):
            revealer_player.known_affiliations = {}

        revealer_player.known_affiliations[target_player.id] = (
            target_player.role.party_membership
        )

        return True


class ChancellorMarkedForExecution(EnablingActPower):
    """Poder de marcado para ejecución del Canciller.

    Permite al Canciller marcar a un jugador para ser ejecutado después
    de que se promulguen 3 políticas fascistas adicionales.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de marcado para ejecución.

        Marca a un jugador específico para ser ejecutado automáticamente
        después de que se promulguen 3 políticas fascistas más.

        Args:
            target_player (Player): El jugador que será marcado para ejecución.
                Puede pasarse como primer argumento en args o como kwarg.

        Returns:
            Player: El jugador marcado para ejecución.
        """
        target_player = args[0] if args else kwargs.get("target_player")

        self.game.state.marked_for_execution = target_player
        self.game.state.marked_for_execution_tracker = (
            self.game.state.board.fascist_track
        )

        self.game.logger.log(
            f"Player {target_player.id} ({target_player.name}) has been marked for execution by Chancellor {self.game.state.chancellor.name}."
        )
        self.game.logger.log(
            f"Current fascist track is {self.game.state.board.fascist_track}. They will be executed after 3 more fascist policies are enacted if not pardoned."
        )

        return target_player


class ChancellorExecution(EnablingActPower):
    """Poder de ejecución del Canciller.

    Permite al Canciller ejecutar inmediatamente a un jugador,
    eliminándolo permanentemente del juego.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de ejecución inmediata.

        Ejecuta a un jugador específico, marcándolo como muerto y
        eliminándolo de la lista de jugadores activos.

        Args:
            target_player (Player): El jugador que será ejecutado.
                Puede pasarse como primer argumento en args o como kwarg.

        Returns:
            Player: El jugador ejecutado.
        """
        target_player = args[0] if args else kwargs.get("target_player")

        target_player.is_dead = True

        if target_player in self.game.state.active_players:
            self.game.state.active_players.remove(target_player)

        return target_player


class VoteOfNoConfidence(EnablingActPower):
    """Poder de voto de no confianza del Canciller.

    Permite al Canciller promulgar la última política descartada,
    proporcionando una segunda oportunidad para políticas previamente rechazadas.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de voto de no confianza.

        Promulga la última política que fue descartada, dándole
        una segunda oportunidad de ser implementada.

        Returns:
            Policy or None: La política promulgada, o None si no hay
                políticas descartadas disponibles.
        """
        if not self.game.state.last_discarded:
            return None

        policy = self.game.state.last_discarded
        self.game.state.board.enact_policy(policy)

        return policy
