"""Jugador controlado por IA para Secret Hitler XL.

Este módulo define la clase AIPlayer que representa un jugador controlado
por inteligencia artificial con estrategias automatizadas.
"""

from random import choice

from src.players.abstract_player import Player
from src.players.strategies import (
    CommunistStrategy,
    FascistStrategy,
    LiberalStrategy,
    RandomStrategy,
    SmartStrategy,
)


class AIPlayer(Player):
    """Jugador controlado por IA que utiliza estrategias para tomar decisiones.

    Extiende la clase Player para proporcionar comportamiento automatizado
    basado en diferentes estrategias de juego.
    """

    def __init__(self, player_id, name, role, state, strategy_type="role"):
        """Inicializa un jugador IA.

        Args:
            player_id (int): ID único del jugador.
            name (str): Nombre del jugador.
            role: Rol asignado al jugador.
            state: Estado actual del juego.
            strategy_type (str): Tipo de estrategia a utilizar.
        """
        super().__init__(player_id, name, role, state)
        self.peeked_policies = None

        if isinstance(role, str):
            from src.roles.role import Communist, Fascist, Hitler, Liberal

            if role == "liberal":
                role = Liberal()
            elif role == "fascist":
                role = Fascist()
            elif role == "communist":
                role = Communist()
            elif role == "hitler":
                role = Hitler()
            self.role = role

        if role is None:
            self.strategy = RandomStrategy(self)
            return

        if strategy_type == "random":
            self.strategy = RandomStrategy(self)
        elif strategy_type == "smart":
            self.strategy = SmartStrategy(self)
        else:
            if self.is_fascist or self.is_hitler:
                self.strategy = FascistStrategy(self)
            elif self.is_communist:
                self.strategy = CommunistStrategy(self)
            else:
                self.strategy = LiberalStrategy(self)

    def nominate_chancellor(self, eligible_players=None):
        """Nomina un canciller.

        Args:
            eligible_players (list, optional): Lista de jugadores elegibles.

        Returns:
            Player: El jugador nominado como canciller.
        """
        if eligible_players is None:
            eligible_players = self.state.get_eligible_chancellors()
        return self.strategy.nominate_chancellor(eligible_players)

    def filter_policies(self, policies):
        """Filtra políticas como presidente.

        Args:
            policies (list): Lista de 3 políticas.

        Returns:
            tuple: (políticas elegidas [2], política descartada [1]).
        """
        return self.strategy.filter_policies(policies)

    def choose_policy(self, policies):
        """Elige qué política promulgar como canciller.

        Args:
            policies (list): Lista de 2 políticas.

        Returns:
            tuple: (política elegida [1], política descartada [1]).
        """
        return self.strategy.choose_policy(policies)

    def vote(self):
        """Vota sobre un gobierno.

        Returns:
            bool: True para Ja, False para Nein.
        """
        return self.strategy.vote(
            self.state.president_candidate, self.state.chancellor_candidate
        )

    def veto(self):
        """Decide si vetar como canciller.

        Returns:
            bool: True para vetar, False en caso contrario.
        """
        policies = self.state.current_policies
        return self.strategy.veto(policies)

    def accept_veto(self):
        """Decide si aceptar el veto como presidente.

        Returns:
            bool: True para aceptar el veto, False en caso contrario.
        """
        policies = self.state.current_policies
        return self.strategy.accept_veto(policies)

    def view_policies(self, policies):
        """Ve políticas durante el espionaje.

        Args:
            policies (list): Lista de políticas vistas.
        """
        self.peeked_policies = policies

    def policy_peek(self, policies):
        """Reacciona a ver políticas con espionaje de políticas.

        Args:
            policies (list): Lista de políticas vistas.
        """
        self.peeked_policies = policies

    def kill(self):
        """Elige un jugador para ejecutar.

        Returns:
            Player: El jugador elegido para ejecutar.
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_kill(eligible_players)

    def choose_player_to_mark(self):
        """Elige un jugador para marcar para ejecución.

        Returns:
            Player: El jugador elegido para marcar.
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_mark(eligible_players)

    def inspect_player(self):
        """Elige un jugador para inspeccionar.

        Returns:
            Player: El jugador elegido para inspeccionar.
        """
        uninspected = [
            p
            for p in self.state.active_players
            if p != self and p.id not in self.inspected_players
        ]

        eligible_players = (
            uninspected
            if uninspected
            else [p for p in self.state.active_players if p != self]
        )
        return self.strategy.choose_player_to_inspect(eligible_players)

    def choose_next(self):
        """Elige el próximo presidente en elección especial.

        Returns:
            Player: El jugador elegido como próximo presidente.
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_next_president(eligible_players)

    def choose_player_to_radicalize(self):
        """Elige un jugador para convertir al comunismo.

        Returns:
            Player: El jugador elegido para radicalizar.
        """
        eligible_players = [
            p for p in self.state.active_players if p != self and not p.is_hitler
        ]
        return self.strategy.choose_player_to_radicalize(eligible_players)

    def propaganda_decision(self, policy):
        """Decide si descartar la política superior.

        Args:
            policy: La política superior del mazo.

        Returns:
            bool: True para descartar, False para mantener.
        """
        if self.is_liberal:
            return policy.type == "fascist"
        elif self.is_fascist or self.is_hitler:
            return policy.type == "liberal"
        elif self.is_communist:
            return policy.type == "fascist"
        else:
            return False

    def choose_revealer(self, eligible_players):
        """Elige un jugador para revelar afiliación política.

        Args:
            eligible_players (list): Jugadores elegibles.

        Returns:
            Player: El jugador elegido para revelar afiliación.
        """
        # Choose a trusted player based on role
        if self.is_liberal:
            # Choose another liberal if known
            liberals = [
                p
                for p in eligible_players
                if p != self
                and p.id in self.inspected_players
                and self.inspected_players[p.id] == "liberal"
            ]
            if liberals:
                return choice(liberals)

        elif self.is_fascist or self.is_hitler:
            fascists = [
                p for p in self.state.active_players if p != self and p.is_fascist
            ]
            if fascists:
                return choice(fascists)
        elif self.is_communist:
            communists = [
                p
                for p in self.state.active_players
                if p != self and p.id in self.known_communists
            ]
            if communists:
                return choice(communists)

        eligible_players = [p for p in self.state.active_players if p != self]
        return choice(eligible_players)

    def social_democratic_removal_choice(self, state):
        """Elige qué pista de políticas eliminar (Socialdemócrata).

        Args:
            state: Estado actual del juego.

        Returns:
            str: "fascist" o "communist".
        """
        if (self.is_liberal or self.is_communist) and state.fascist_track > 0:
            return "fascist"
        elif (self.is_fascist or self.is_hitler) and state.communist_track > 0:
            return "communist"
        else:
            return choice(["fascist", "communist"])

    def pardon_player(self):
        """Decide si perdonar a un jugador marcado para ejecución.

        Returns:
            bool: True para perdonar, False en caso contrario.
        """
        if not hasattr(self.strategy, "pardon_player"):
            if (
                (self.is_fascist or self.is_hitler)
                and self.state.marked_for_execution is not None
                and self.state.marked_for_execution.is_hitler
            ):
                return True
            return False
        return self.strategy.pardon_player()

    def choose_player_to_bug(self, eligible_players):
        """Elige un jugador para espiar su afiliación política.

        Args:
            eligible_players (list): Jugadores elegibles para espiar.

        Returns:
            Player: El jugador elegido para espiar.
        """
        return self.strategy.choose_player_to_bug(eligible_players)

    def mark_for_execution(self, eligible_players=None):
        """Elige un jugador para marcar para ejecución.

        Args:
            eligible_players (list, optional): Jugadores que pueden ser marcados.

        Returns:
            Player: El jugador elegido para marcar.
        """
        if eligible_players is None:
            eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_mark(eligible_players)

    def chancellor_veto_proposal(self, policies):
        """Como canciller, decide si proponer un veto.

        Args:
            policies (list): Lista de 2 políticas.

        Returns:
            bool: True para proponer veto, False para promulgar política.
        """
        if not self.state.veto_available:
            return False
        return self.strategy.chancellor_veto_proposal(policies)

    def vote_of_no_confidence(self):
        """Como canciller con poder de Ley Habilitante, decide si promulgar la política descartada.

        Returns:
            bool: True para promulgar política descartada, False para dejarla.
        """
        return self.strategy.vote_of_no_confidence()

    def chancellor_propose_veto(self, policies):
        """El canciller propone un veto cuando está disponible.

        Args:
            policies (list): Lista de 2 políticas que recibió el canciller.

        Returns:
            bool: True para proponer veto, False en caso contrario.
        """
        if not self.state.veto_available:
            return False
        return self.strategy.chancellor_veto_proposal(policies)

    def choose_player_to_mark_for_execution(self):
        """Elige un jugador para marcar para ejecución futura.

        Returns:
            Player: El jugador a marcar.
        """
        eligible_players = [p for p in self.state.active_players if p != self]
        return self.strategy.choose_player_to_mark(eligible_players)

    def choose_to_pardon(self):
        """Elige si perdonar al jugador marcado para ejecución.

        Returns:
            bool: True para perdonar, False en caso contrario.
        """
        return self.strategy.pardon_player()

    def no_confidence_decision(self):
        """Decide si promulgar la política descartada (Voto de No Confianza).

        Returns:
            bool: True para promulgar, False en caso contrario.
        """
        return self.strategy.vote_of_no_confidence()

    def choose_player_to_investigate(self, eligible_players):
        """Elige un jugador para investigar su afiliación política.

        Args:
            eligible_players (list): Jugadores que pueden ser investigados.

        Returns:
            Player: El jugador a investigar.
        """
        return self.strategy.choose_player_to_inspect(eligible_players)

    def choose_next_president(self, eligible_players):
        """Elige el próximo presidente para elección especial.

        Args:
            eligible_players (list): Jugadores que pueden ser elegidos como próximo presidente.

        Returns:
            Player: El jugador que será el próximo presidente.
        """
        return self.strategy.choose_next_president(eligible_players)
