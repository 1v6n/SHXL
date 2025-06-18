"""Rutas de gestión del juego.

Este módulo define las rutas de la API Flask para manejar la gestión
del juego, incluyendo creación, unión, inicio y consulta de estado.
"""

import uuid

from flask import Blueprint, jsonify, request

from src.game.game import SHXLGame
from src.players.player_factory import PlayerFactory

from ..storage import games
from ..utils.game_state_helpers import (
    _get_board_info,
    _get_current_phase_info,
    _get_current_timestamp,
    _get_game_config_info,
    _get_game_state_status,
    _get_government_info,
    _get_last_action_info,
    _get_nomination_info,
    _get_players_info,
    _get_trackers_info,
)

game_bp = Blueprint("game", __name__)


@game_bp.route("/newgame", methods=["POST"])
def create_new_game():
    """Crea una nueva sala de juego SHXL.

    Recibe los parámetros de configuración del juego y crea una nueva instancia
    de SHXLGame. La sala se crea vacía, esperando que los jugadores se unan
    antes de que comience la partida.

    Returns:
        tuple: Una tupla con la respuesta JSON y el código de estado HTTP.
            La respuesta contiene:
            - gameID (str): Identificador único de la partida (8 caracteres)
            - maxPlayers (int): Número máximo de jugadores permitidos
            - state (str): Estado actual del juego ("waiting_for_players")
            - currentPlayers (int): Número actual de jugadores (siempre 0 al crear)

    Request JSON:
        playerCount (int, optional): Número máximo de jugadores (default: 10)
        withCommunists (bool, optional): Incluir roles comunistas (default: False)
        withAntiPolicies (bool, optional): Incluir políticas anti (default: False)
        withEmergencyPowers (bool, optional): Incluir poderes de emergencia (default: False)
        strategy (str, optional): Estrategia de IA para jugadores bot (default: "role")
    """
    data = request.json
    player_count = data.get("playerCount", 10)
    include_communists = data.get("withCommunists", False)
    with_anti_policies = data.get("withAntiPolicies", False)
    with_emergency_powers = data.get("withEmergencyPowers", False)
    strategy = data.get("strategy", "role")

    game_id = str(uuid.uuid4())[:8]
    game = SHXLGame()

    game.player_count = player_count
    game.include_communists = include_communists
    game.with_anti_policies = with_anti_policies
    game.with_emergency_powers = with_emergency_powers
    game.ai_strategy = strategy

    game.state.player_factory = PlayerFactory()
    game.state.players = []

    games[game_id] = game

    return (
        jsonify(
            {
                "gameID": game_id,
                "maxPlayers": player_count,
                "state": "waiting_for_players",
                "currentPlayers": 0,
            }
        ),
        201,
    )


@game_bp.route("/games/<game_id>/join", methods=["POST"])
def join_game(game_id):
    """Permite a un jugador unirse a una sala de juego existente.

    Valida que la sala exista, tenga espacio disponible y no haya comenzado
    la partida. Crea un nuevo jugador humano y lo agrega a la lista de
    participantes.

    Args:
        game_id (str): Identificador único de la sala de juego

    Returns:
        tuple: Una tupla con la respuesta JSON y el código de estado HTTP.
            En caso de éxito (200):
            - playerId (int): ID único del jugador dentro de la partida
            - currentPlayers (int): Número actual de jugadores en la sala
            - maxPlayers (int): Número máximo de jugadores permitidos

            En caso de error (400/403/404):
            - error (str): Descripción del error ocurrido

    Request JSON:
        playerName (str): Nombre del jugador que se quiere unir

    Raises:
        400: Si no se proporciona playerName
        403: Si la sala está llena o el juego ya comenzó
        404: Si la sala no existe
    """
    data = request.get_json()
    player_name = data.get("playerName")

    if not player_name:
        return jsonify({"error": "Missing playerName"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if game.state.president is not None:
        return jsonify({"error": "Game already in progress"}), 403

    if len(game.state.players) >= game.player_count:
        return jsonify({"error": "Game is full"}), 403

    new_id = len(game.state.players)
    player = game.state.player_factory.create_player(
        id=new_id,
        name=player_name,
        role=None,
        state=game.state,
        strategy_type="smart",
        player_type="human",
    )
    game.state.players.append(player)

    return (
        jsonify(
            {
                "playerId": player.id,
                "currentPlayers": len(game.state.players),
                "maxPlayers": game.player_count,
            }
        ),
        200,
    )


@game_bp.route("/games/<game_id>/start", methods=["POST"])
def start_game(game_id):
    """Inicia una sesión de juego cuando el host decide que todos los jugadores están listos.

    Valida que el host tenga permisos, que haya suficientes jugadores y configura
    el juego con roles asignados. Solo el jugador con ID 0 (host) puede iniciar la partida.

    Args:
        game_id (str): Identificador único del juego a iniciar.

    Returns:
        tuple: Una tupla con la respuesta JSON y el código de estado HTTP.
            En caso de éxito (200):
            - message (str): Mensaje de confirmación
            - gameState (str): Estado del juego ("in_progress")
            - currentPlayers (int): Número de jugadores actuales
            - roles_assigned (bool): Si los roles fueron asignados
            - deck_ready (bool): Si el mazo está preparado
            - playersPreserved (bool): Si los jugadores se preservaron
            - initialPresident (dict): Información del presidente inicial
            - playerTypes (list): Tipos de todos los jugadores

            En caso de error (400/403/404/500):
            - error (str): Descripción del error

    Request JSON:
        hostPlayerID (int): ID del jugador que intenta iniciar el juego. Debe ser 0 (host).

    Note:
        Respuestas de error:
        - 400: hostPlayerID faltante en el cuerpo de la petición.
        - 403: Solo el host puede iniciar, no hay jugadores, juego ya en progreso,
               o no hay suficientes jugadores.
        - 404: Juego con el game_id dado no existe.
        - 500: Falló al asignar presidente inicial u otros errores inesperados.
    """

    data = request.get_json()
    host_player_id = data.get("hostPlayerID")

    if host_player_id is None:
        return jsonify({"error": "Missing hostPlayerID"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if host_player_id != 0:
        return jsonify({"error": "Only the host can start the game"}), 403

    if len(game.state.players) == 0:
        return jsonify({"error": "No players in the game"}), 403

    if hasattr(game.state, "game_state") and game.state.game_state == "in_progress":
        return jsonify({"error": "Game already in progress"}), 403

    min_players = 5
    if len(game.state.players) < min_players:
        return jsonify({"error": f"Need at least {min_players} players to start"}), 403

    try:

        human_players_info = []
        for player in game.state.players:
            human_players_info.append(
                {
                    "id": player.id,
                    "name": getattr(player, "name", f"Player {player.id}"),
                    "player_type": getattr(player, "player_type", "human"),
                }
            )

        game.setup_game(
            player_count=len(human_players_info),
            with_communists=game.include_communists,
            with_anti_policies=game.with_anti_policies,
            with_emergency_powers=game.with_emergency_powers,
            ai_strategy=game.ai_strategy,
        )

        for i, player_info in enumerate(human_players_info):
            if i < len(game.state.players):
                game_player = game.state.players[i]
                game_player.name = player_info["name"]
                game_player.player_type = player_info["player_type"]
                game_player.id = player_info["id"]

        initial_president = game.state.president
        if not initial_president:
            return jsonify({"error": "Failed to assign initial president"}), 500

        return (
            jsonify(
                {
                    "message": "Game started successfully",
                    "gameState": "in_progress",
                    "currentPlayers": len(game.state.players),
                    "roles_assigned": True,
                    "deck_ready": True,
                    "playersPreserved": True,
                    "initialPresident": {
                        "id": initial_president.id,
                        "name": getattr(
                            initial_president, "name", f"Player {initial_president.id}"
                        ),
                        "isHuman": getattr(initial_president, "player_type", "human")
                        == "human",
                    },
                    "playerTypes": [
                        {
                            "id": p.id,
                            "name": getattr(p, "name", f"Player {p.id}"),
                            "isHuman": getattr(p, "player_type", "human") == "human",
                        }
                        for p in game.state.players
                    ],
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to start game: {str(e)}"}), 500


@game_bp.route("/games/<game_id>/state", methods=["GET"])
def get_game_state(game_id):
    """Consulta el estado actual del juego para actualizar la interfaz.

    Proporciona información completa del estado del juego incluyendo jugadores,
    gobierno actual, nominaciones, trackers y última acción. Los roles secretos
    se ocultan a jugadores no autorizados.

    Args:
        game_id (str): Identificador único de la sala de juego

    Query Parameters:
        playerId (int, optional): ID del jugador que consulta (para filtrar información sensible)

    Returns:
        tuple: Una tupla con la respuesta JSON y el código de estado HTTP.
            En caso de éxito (200):
            - gameState (str): Estado actual del juego
            - currentPhase (str): Fase actual del juego
            - players (list): Lista de jugadores con información visible
            - government (dict): Información del gobierno actual
            - nomination (dict): Información de nominación actual
            - trackers (dict): Estados de los trackers del juego
            - board (dict): Estado del tablero de políticas
            - lastAction (dict): Información de la última acción
            - gameConfig (dict): Configuración del juego

            En caso de error (404):
            - error (str): Descripción del error
    """
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    requesting_player_id = request.args.get("playerId", type=int)

    try:
        game_state = {
            "gameState": _get_game_state_status(game),
            "currentPhase": _get_current_phase_info(game),
            "players": _get_players_info(game, requesting_player_id),
            "government": _get_government_info(game),
            "nomination": _get_nomination_info(game),
            "trackers": _get_trackers_info(game),
            "board": _get_board_info(game),
            "lastAction": _get_last_action_info(game),
            "gameConfig": _get_game_config_info(game),
            "gameId": game_id,
            "timestamp": _get_current_timestamp(),
        }

        return jsonify(game_state), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get game state: {str(e)}"}), 500


@game_bp.route("/games/<game_id>/add-bots", methods=["POST"])
def add_bots(game_id):
    """Agrega múltiples bots a la sala de juego.

    Permite al host agregar jugadores IA a la partida antes de que comience.
    Los bots se crean con la estrategia especificada y nombres generados
    automáticamente.

    Args:
        game_id (str): Identificador único del juego.

    Returns:
        tuple: Una tupla con la respuesta JSON y el código de estado HTTP.
            En caso de éxito (200):
            - message (str): Mensaje de confirmación
            - addedBots (list): Lista de bots agregados con sus detalles
            - currentPlayers (int): Número actual de jugadores
            - maxPlayers (int): Número máximo de jugadores

            En caso de error (400/403/404):
            - error (str): Descripción del error

    Request JSON:
        count (int): Número de bots a agregar (1-10).
        strategy (str, optional): Estrategia para todos los bots (default: "smart").
        namePrefix (str, optional): Prefijo para nombres de bots (default: "Bot").

    Note:
        - Solo se pueden agregar bots antes de que inicie la partida.
        - El número de bots no puede exceder los espacios disponibles.
        - Los nombres se generan como "{namePrefix}_{número}".
    """
    data = request.get_json()
    bot_count = data.get("count", 1)
    strategy = data.get("strategy", "smart")
    name_prefix = data.get("namePrefix", "Bot")

    if bot_count < 1 or bot_count > 10:
        return jsonify({"error": "Bot count must be between 1 and 10"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if game.state.president is not None:
        return jsonify({"error": "Game already in progress"}), 403

    available_spots = game.player_count - len(game.state.players)
    if bot_count > available_spots:
        return jsonify({"error": f"Only {available_spots} spots available"}), 403

    added_bots = []

    for _ in range(bot_count):
        new_id = len(game.state.players)
        bot_name = f"{name_prefix}_{new_id + 1}"

        bot = game.state.player_factory.create_player(
            id=new_id,
            name=bot_name,
            role=None,
            state=game.state,
            strategy_type=strategy,
            player_type="ai",
        )
        game.state.players.append(bot)

        added_bots.append(
            {"playerId": bot.id, "playerName": bot_name, "strategy": strategy}
        )

    return (
        jsonify(
            {
                "message": f"Added {bot_count} bots successfully",
                "addedBots": added_bots,
                "currentPlayers": len(game.state.players),
                "maxPlayers": game.player_count,
            }
        ),
        200,
    )
