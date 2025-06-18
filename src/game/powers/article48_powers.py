from src.game.powers.abstract_power import Power, PowerOwner


class Article48Power(Power):
    """Clase base para los poderes del Artículo 48 (poderes de emergencia del Presidente).

    Esta clase define la estructura común para todos los poderes especiales que puede
    ejercer el Presidente cuando se activa el Artículo 48 en el juego.
    """

    @staticmethod
    def get_owner():
        """Obtiene el propietario de este poder.

        Returns:
            PowerOwner: El propietario del poder (PRESIDENT).
        """
        return PowerOwner.PRESIDENT


class PresidentialPropaganda(Article48Power):
    """Poder de propaganda presidencial.

    Permite al Presidente ver la carta superior del mazo y opcionalmente descartarla
    para influir en las políticas que se van a promulgar.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de propaganda presidencial.

        El Presidente puede ver la carta superior del mazo de políticas y decidir
        si la descarta o la mantiene en el mazo para influir en futuras decisiones.

        Returns:
            Policy or None: La política vista, o None si no hay políticas disponibles.
        """
        if not self.game.state.board.policies:
            return None

        policy = self.game.state.board.policies[0]
        discard = self.game.state.president.propaganda_decision(policy)

        if discard:
            self.game.state.board.policies.pop(0)
            self.game.state.board.discard(policy)

        return policy


class PresidentialPolicyPeek(Article48Power):
    """Poder de inspección de políticas presidencial.

    Permite al Presidente ver las tres cartas superiores del mazo de políticas
    sin extraerlas, proporcionando información estratégica sobre las próximas políticas.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de inspección de políticas presidencial.

        Permite al Presidente examinar las tres cartas superiores del mazo
        de políticas para obtener información estratégica sin modificar el orden.

        Returns:
            list: Lista con las tres políticas superiores del mazo.
        """
        top_policies = self.game.state.board.policies[:3]
        return top_policies


class PresidentialImpeachment(Article48Power):
    """Poder de acusación presidencial.

    Permite al Presidente forzar al Canciller a revelar su afiliación partidaria
    a un jugador específico elegido por el Presidente.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de acusación presidencial.

        El Presidente puede forzar al Canciller a revelar su afiliación partidaria
        a un jugador específico. Si no se especifica el receptor, el Presidente
        debe elegir uno de los jugadores elegibles.

        Args:
            target_player (Player): El jugador que debe revelar su afiliación
                (típicamente el Canciller). Puede pasarse como primer argumento
                en args o como kwarg.
            revealer_player (Player, optional): El jugador que verá la afiliación.
                Si no se proporciona, el Presidente debe elegir uno. Puede pasarse
                como segundo argumento en args o como kwarg.

        Returns:
            bool: True si la operación fue exitosa, False en caso contrario.
        """
        if len(args) >= 1:
            target_player = args[0]
            revealer_player = (
                args[1] if len(args) >= 2 else kwargs.get("revealer_player")
            )
        else:
            target_player = kwargs.get("target_player")
            revealer_player = kwargs.get("revealer_player")

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


class PresidentialMarkedForExecution(Article48Power):
    """Poder presidencial de marcado para ejecución.

    Permite al Presidente marcar a un jugador para ser ejecutado después
    de que se promulguen 3 políticas fascistas adicionales.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder presidencial de marcado para ejecución.

        Marca a un jugador específico para ser ejecutado automáticamente
        después de que se promulguen 3 políticas fascistas más, a menos
        que sea perdonado posteriormente.

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
            f"Player {target_player.id} ({target_player.name}) has been marked for execution."
        )
        self.game.logger.log(
            f"Current fascist track is {self.game.state.board.fascist_track}. They will be executed after 3 more fascist policies are enacted if not pardoned."
        )

        return target_player


class PresidentialExecution(Article48Power):
    """Poder de ejecución presidencial.

    Permite al Presidente ejecutar inmediatamente a un jugador,
    eliminándolo permanentemente del juego.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de ejecución presidencial inmediata.

        Ejecuta a un jugador específico, marcándolo como muerto y
        eliminándolo de la lista de jugadores activos de forma permanente.

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


class PresidentialPardon(Article48Power):
    """Poder de perdón presidencial.

    Permite al Presidente perdonar a un jugador que había sido previamente
    marcado para ejecución, salvándolo de la muerte automática.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de perdón presidencial.

        Perdona a un jugador que había sido marcado para ejecución,
        eliminando la marca y salvándolo de la muerte automática cuando
        se promulguen las políticas fascistas restantes.

        Returns:
            Player or None: El jugador perdonado, o None si no había ningún
                jugador marcado para ejecución.
        """
        if not self.game.state.marked_for_execution:
            self.game.logger.log("No player is currently marked for execution.")
            return None

        pardoned = self.game.state.marked_for_execution
        self.game.logger.log(
            f"Player {pardoned.id} ({pardoned.name}) has been pardoned from execution."
        )

        self.game.state.marked_for_execution = None
        self.game.state.marked_for_execution_tracker = None

        return pardoned
