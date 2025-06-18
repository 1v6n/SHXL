"""Módulo que implementa los poderes específicos de la facción fascista.

Este módulo contiene las clases que representan los poderes especiales
que los fascistas pueden usar durante el juego para investigar,
manipular y eliminar jugadores.
"""

from src.game.powers.abstract_power import Power


class InvestigateLoyalty(Power):
    """Poder que permite investigar la lealtad de partido de un jugador."""

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de investigar la lealtad de un jugador.

        Args:
            target_player: El jugador objetivo para investigar.

        Returns:
            str: La afiliación de partido del jugador objetivo.
        """
        target_player = args[0]

        self.game.state.investigated_players.append(target_player)

        return target_player.role.party_membership


class SpecialElection(Power):
    """Poder que permite establecer un presidente especial para la próxima elección."""

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de elección especial.

        Args:
            next_president: El jugador que será el próximo presidente.

        Returns:
            Player: El jugador seleccionado como próximo presidente.
        """
        next_president = args[0]

        self.game.state.special_election_return_index = self.game.state.president.id

        self.game.state.special_election = True
        self.game.state.president_candidate = next_president

        return next_president


class PolicyPeek(Power):
    """Poder que permite ver las próximas 3 políticas de la pila de robo."""

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de espiar políticas.

        Returns:
            list: Las 3 políticas superiores de la pila.
        """
        top_policies = self.game.state.board.policies[:3]

        return top_policies


class Execution(Power):
    """Poder que permite ejecutar a un jugador eliminándolo del juego."""

    def execute(self, *args, **kwargs):
        """Ejecuta el poder de ejecución.

        Args:
            target_player: El jugador a ejecutar.

        Returns:
            Player: El jugador ejecutado.
        """
        target_player = args[0]

        target_player.is_dead = True

        if target_player in self.game.state.active_players:
            self.game.state.active_players.remove(target_player)

        return target_player
