"""
SHXL Game API Server

Este módulo proporciona una API REST para crear y gestionar partidas del juego SHXL.
Permite crear nuevas salas de juego y que los jugadores se unan a ellas.
"""

import uuid

from flask import Flask, jsonify, request

from src.game.game import SHXLGame
from src.players.player_factory import PlayerFactory

app = Flask(__name__)
games = {}


@app.route("/newgame", methods=["POST"])
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
        withCommunists (bool, optional): Incluir roles comunistas (default: True)
        withAntiPolicies (bool, optional): Incluir políticas anti (default: True)
        withEmergencyPowers (bool, optional): Incluir poderes de emergencia (default: True)
        strategy (str, optional): Estrategia de IA para jugadores bot (default: "smart")
    """
    data = request.json
    player_count = data.get("playerCount", 10)
    include_communists = data.get("withCommunists", True)
    with_anti_policies = data.get("withAntiPolicies", True)
    with_emergency_powers = data.get("withEmergencyPowers", True)
    strategy = data.get("strategy", "smart")

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


@app.route("/games/<game_id>/join", methods=["POST"])
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


@app.route("/games/<game_id>/start", methods=["POST"])
def start_game(game_id):
    """Inicia una partida cuando el anfitrión decide que están todos listos."""
    data = request.get_json()
    host_player_id = data.get("hostPlayerID")

    if host_player_id is None:
        return jsonify({"error": "Missing hostPlayerID"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Verificar que el solicitante es el anfitrión (primer jugador, ID = 0)
    if host_player_id != 0:
        return jsonify({"error": "Only the host can start the game"}), 403

    # Verificar que hay al menos un jugador (el anfitrión)
    if len(game.state.players) == 0:
        return jsonify({"error": "No players in the game"}), 403

    # Verificar que el anfitrión existe
    host_player = next((p for p in game.state.players if p.id == 0), None)
    if not host_player:
        return jsonify({"error": "Host player not found"}), 403

    # Verificar que el juego no haya comenzado ya
    if hasattr(game.state, "game_state") and game.state.game_state == "in_progress":
        return jsonify({"error": "Game already in progress"}), 403

    if game.state.president is not None:
        return jsonify({"error": "Game already in progress"}), 403

    # Verificar mínimo de jugadores (SHXL requiere al menos 5)
    min_players = 5
    if len(game.state.players) < min_players:
        return jsonify({"error": f"Need at least {min_players} players to start"}), 403

    try:
        # 🔧 ESTRATEGIA CORRECTA: Usar human_player_indices

        # 1. Guardar información de jugadores humanos existentes
        human_players_info = []
        for player in game.state.players:
            human_players_info.append({"id": player.id, "name": player.name})

        # 2. Crear lista de índices de jugadores humanos
        human_indices = [p["id"] for p in human_players_info]

        # 3. Llamar setup_game con los parámetros correctos
        game.setup_game(
            player_count=game.player_count,
            with_communists=game.include_communists,
            with_anti_policies=game.with_anti_policies,
            with_emergency_powers=game.with_emergency_powers,
            human_player_indices=human_indices,  # ✅ Parámetro correcto
            ai_strategy=game.ai_strategy,
        )

        # 4. Restaurar nombres de jugadores humanos
        for human_info in human_players_info:
            player_id = human_info["id"]
            if player_id < len(game.state.players):
                game.state.players[player_id].name = human_info["name"]

        # 5. Cambiar estado del juego
        game.state.game_state = "in_progress"

        return (
            jsonify(
                {
                    "message": "Game started successfully",
                    "state": "in_progress",
                    "currentPlayers": len(game.state.players),
                    "roles_assigned": True,
                    "deck_ready": True,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Failed to start game: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint de health check para verificar el estado del servidor.

    Proporciona una forma simple de verificar que el servidor API está
    funcionando correctamente.

    Returns:
        tuple: Una tupla con la respuesta JSON y el código de estado HTTP (200).
            La respuesta contiene:
            - status (str): Estado del servidor ("OK")
            - message (str): Mensaje descriptivo
    """
    return jsonify({"status": "OK", "message": "Server is running"}), 200


if __name__ == "__main__":
    """Punto de entrada principal del servidor.

    Inicia el servidor Flask en modo desarrollo con debug habilitado.
    El servidor escucha en 127.0.0.1:5000 por defecto.
    """
    app.run(host="127.0.0.1", port=5000, debug=True)
