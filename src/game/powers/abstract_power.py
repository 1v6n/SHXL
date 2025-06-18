from abc import ABC, abstractmethod
from enum import Enum, auto


class PowerOwner(Enum):
    """Tipos de propietarios de poderes.

    Esta enumeración define los diferentes tipos de jugadores que pueden
    ser propietarios y ejecutores de poderes especiales en el juego.
    """

    PRESIDENT = auto()
    CHANCELLOR = auto()


class Power(ABC):
    """Clase base abstracta para todos los poderes del juego.

    Define la interfaz común que deben implementar todos los poderes especiales,
    incluyendo poderes fascistas, comunistas y del Acta Habilitante.
    """

    def __init__(self, game):
        """Inicializa el poder con una referencia al juego.

        Args:
            game (Game): La instancia del juego que contiene el estado actual.
        """
        self.game = game

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Ejecuta el poder especial.

        Este método debe ser implementado por todas las subclases para definir
        la funcionalidad específica de cada poder.
          Args:
            *args: Argumentos posicionales variables según el poder específico.
            **kwargs: Argumentos nombrados variables según el poder específico.

        Returns:
            El tipo de retorno varía según la implementación específica del poder.
        """

    @staticmethod
    def get_owner():
        """Obtiene el propietario por defecto de este poder.

        Returns:
            PowerOwner: El propietario del poder (por defecto PRESIDENT).
        """
        return PowerOwner.PRESIDENT


class InvestigateLoyalty(Power):
    """Poder fascista de investigación de lealtad.

    Permite investigar la afiliación partidaria de un jugador objetivo,
    revelando su membresía política al ejecutor del poder.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta la investigación de lealtad.

        Investiga la afiliación partidaria de un jugador específico y
        marca al jugador como investigado en el estado del juego.

        Args:
            target_player (Player): El jugador que será investigado.
                Puede pasarse como primer argumento en args o como kwarg.

        Returns:
            str: La afiliación partidaria del jugador objetivo.
        """
        target_player = args[0] if args else kwargs.get("target_player")

        self.game.state.investigated_players.append(target_player)
        return target_player.role.party_membership


class SpecialElection(Power):
    """Poder fascista de elección especial.

    Permite al ejecutor designar al siguiente Presidente para una elección especial,
    alterando temporalmente el orden normal de la presidencia.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta la elección especial.

        Establece al siguiente Presidente para una elección especial,
        guardando el índice actual para restaurar el orden después.

        Args:
            next_president (Player): El jugador que será el próximo Presidente.
                Puede pasarse como primer argumento en args o como kwarg.

        Returns:
            Player: El jugador seleccionado como próximo Presidente.
        """
        next_president = args[0] if args else kwargs.get("next_president")

        self.game.state.special_election_return_index = self.game.state.president.id
        self.game.state.special_election = True
        self.game.state.president_candidate = next_president

        return next_president


class PolicyPeek(Power):
    """Poder fascista de inspección de políticas.

    Permite examinar las tres cartas superiores del mazo de políticas
    sin extraerlas, proporcionando información estratégica.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta la inspección de políticas.

        Examina las tres cartas superiores del mazo de políticas
        sin modificar su orden ni extraerlas del mazo.

        Returns:
            list: Lista con las tres políticas superiores del mazo.
        """
        top_policies = self.game.state.board.policies[:3]
        return top_policies


class Execution(Power):
    """Poder fascista de ejecución.

    Permite ejecutar inmediatamente a un jugador, eliminándolo
    permanentemente del juego.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta la ejecución de un jugador.

        Mata al jugador objetivo y lo elimina de la lista de jugadores activos,
        sacándolo permanentemente del juego.

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


class Confession(Power):
    """Poder comunista de confesión.

    Permite al Presidente revelar públicamente su afiliación partidaria,
    creando transparencia sobre su identidad política.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta la confesión del Presidente.

        El Presidente revela públicamente su afiliación partidaria,
        registrando esta información en las afiliaciones reveladas del juego.

        Returns:
            str: La afiliación partidaria del Presidente.
        """
        president = self.game.state.president
        self.game.state.revealed_affiliations[president.id] = (
            president.role.party_membership
        )

        return president.role.party_membership


class Bugging(Power):
    """Poder comunista de espionaje.

    Permite a los comunistas investigar secretamente la afiliación partidaria
    de otro jugador, compartiendo esta información solo entre comunistas.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el espionaje comunista.

        Los comunistas obtienen información sobre la afiliación partidaria
        de un jugador objetivo, manteniendo esta información secreta
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
    """Poder comunista del Plan Quinquenal.

    Permite manipular el mazo de políticas agregando nuevas cartas comunistas
    y liberales, alterando la distribución de políticas disponibles.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el Plan Quinquenal.

        Agrega 2 políticas comunistas y 1 política liberal al inicio del mazo,
        cambiando las probabilidades de las próximas políticas a promulgar.

        Returns:
            bool: True si la operación fue exitosa.
        """
        from src.policies.policy import Communist, Liberal

        new_policies = [Communist(), Communist(), Liberal()]
        self.game.state.board.policies = new_policies + self.game.state.board.policies

        return True


class Congress(Power):
    """Poder comunista del Congreso.

    Permite a los comunistas identificar a todos los miembros originales del partido,
    útil para verificar conversiones y reorganizar estrategias.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta el Congreso comunista.

        Revela a todos los comunistas quiénes son los miembros originales
        del partido comunista, permitiendo identificar aliados naturales.

        Returns:
            list: Lista de IDs de jugadores que son comunistas originales.
        """
        original_communists = [
            player.id
            for player in self.game.state.players
            if player.role.party_membership == "communist"
        ]

        for player in self.game.state.players:
            if player.role.party_membership == "communist":
                player.known_communists = original_communists

        return original_communists


class Radicalization(Power):
    """Poder comunista de radicalización.

    Permite convertir a un jugador al comunismo, cambiando su afiliación
    partidaria y estrategia política, excepto en casos especiales como Hitler.
    """

    def execute(self, *args, **kwargs):
        """Ejecuta la radicalización de un jugador.

        Convierte a un jugador objetivo al comunismo, cambiando su rol
        político. Hitler y algunos otros roles especiales no pueden ser convertidos.

        Args:
            target_player (Player): El jugador que será radicalizado.
                Puede pasarse como primer argumento en args o como kwarg.

        Returns:
            Player or None: El jugador convertido, o None si la conversión falló.
        """
        target_player = args[0] if args else kwargs.get("target_player")

        if target_player.is_hitler:
            return None

        from src.roles.role import Communist

        target_player.role = Communist()

        return target_player


class Propaganda(Power):
    """Poder comunista de propaganda.

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
    """Poder comunista de acusación.

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
