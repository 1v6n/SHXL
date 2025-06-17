"""
SHXL Game API Server

Este módulo proporciona una API REST para crear y gestionar partidas del juego SHXL.
Permite crear nuevas salas de juego y que los jugadores se unan a ellas.
"""

import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

from src.game.game import SHXLGame
from src.game.phases.election_utils import (
    check_marked_for_execution,
    nominate_chancellor_safe,
    resolve_election,
    run_full_election_cycle,
)
from src.game.phases.legislative_utils import (
    check_veto_proposal,
    draw_presidential_policies,
    end_legislative_session,
    execute_presidential_power,
    handle_chancellor_choice,
    handle_presidential_choice,
    run_full_legislative_cycle,
)
from src.players.player_factory import PlayerFactory

app = Flask(__name__)
games = {}


def _safe_winner_string(winner):
    """Convert winner to safe string format."""
    if isinstance(winner, dict):
        return winner.get("name", winner.get("party", "unknown"))
    elif isinstance(winner, str):
        return winner
    elif winner is None:
        return "unknown"
    elif hasattr(winner, "name"):
        return winner.name
    elif hasattr(winner, "party_membership"):
        return winner.party_membership
    else:
        return str(winner)


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
    """
    Starts a game session when the host decides all players are ready.
    Endpoint: POST /games/<game_id>/start
    Request JSON:
        "hostPlayerID": <int>
    Path Parameters:
        game_id (str): The unique identifier of the game to start.
    Request Body:
        hostPlayerID (int): The ID of the player attempting to start the game. Must be 0 (the host).
    Responses:
        200 OK:
        Game started successfully. Returns game state, initial president, and player info.
        400 Bad Request:
        - Missing hostPlayerID in request body.
        403 Forbidden:
        - Only the host can start the game.
        - No players in the game.
        - Game already in progress.
        - Not enough players to start the game.
        404 Not Found:
        - Game with the given game_id does not exist.
        500 Internal Server Error:
        - Failed to assign initial president or other unexpected errors.
    Returns:
        JSON response with game status, player information, and initial president details.
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


@app.route("/games/<game_id>/nominate", methods=["POST"])
def nominate_chancellor(game_id):
    """
    Handles the chancellor nomination phase in the game.
    This function manages the process of nominating a chancellor, supporting both human and AI players.
    It performs the following steps:
      1. Checks for any pending executions before proceeding with nomination.
      2. Determines if all players are bots; if so, runs the full election cycle automatically.
      3. If at least one human is present, proceeds to individual voting:
         - If the president is human, expects a nomineeId in the request and validates eligibility.
         - If the president is a bot, nominates automatically but still requires human voting.
      4. Handles special cases such as game over or chaos (no eligible chancellors).
    Args:
        game_id (str): The unique identifier for the game.
    Returns:
        Response: A Flask JSON response with the result of the nomination phase, including
                  status messages, nomination details, eligible voters, and phase transitions.
                  Returns appropriate HTTP status codes for errors and success.
    """
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if not hasattr(game.state, "president") or game.state.president is None:
        return jsonify({"error": "No president assigned"}), 403

    current_president = game.state.president

    try:
        execution_result = check_marked_for_execution(game)
        if execution_result["executed"]:
            response_data = {
                "message": f"Player {execution_result['player'].id} was executed before nomination",
                "executionResult": {
                    "executed": True,
                    "playerId": execution_result["player"].id,
                    "playerName": getattr(
                        execution_result["player"],
                        "name",
                        f'Player {execution_result["player"].id}',
                    ),
                },
            }

            if execution_result["game_over"]:
                response_data["gameOver"] = {
                    "winner": execution_result["winner"],
                    "reason": "Hitler was executed",
                }
                response_data["newPhase"] = "game_over"
                return jsonify(response_data), 200

        all_players_are_bots = all(
            getattr(p, "player_type", "human") == "ai"
            for p in game.state.players
            if getattr(p, "is_alive", True)
        )

        if all_players_are_bots:
            full_result = run_full_election_cycle(game)

            return (
                jsonify(
                    {
                        "message": "Full election completed automatically (all bots)",
                        "fullElectionResult": full_result,
                        "newPhase": full_result.get("next_phase", "election"),
                        "gameOver": full_result.get("game_over", False),
                        "winner": (
                            full_result.get("winner")
                            if full_result.get("game_over")
                            else None
                        ),
                    }
                ),
                200,
            )

        data = request.get_json() or {}

        if getattr(current_president, "player_type", "human") == "human":
            nominee_id = data.get("nomineeId")
            if nominee_id is None:
                return jsonify({"error": "Missing nomineeId for human president"}), 400

            nominee = None
            for player in game.state.players:
                if player.id == nominee_id:
                    nominee = player
                    break

            if not nominee:
                return jsonify({"error": "Nominee not found"}), 404

            if hasattr(game.state, "get_eligible_chancellors"):
                eligible_chancellors = game.state.get_eligible_chancellors()
                if nominee not in eligible_chancellors:
                    return (
                        jsonify({"error": "Nominee is not eligible for chancellor"}),
                        403,
                    )

            game.state.chancellor_candidate = nominee
            game.state.current_phase_name = "voting"

            return (
                jsonify(
                    {
                        "message": "Chancellor nominated by human president",
                        "nomination": {
                            "president": {
                                "id": current_president.id,
                                "name": getattr(
                                    current_president,
                                    "name",
                                    f"Player {current_president.id}",
                                ),
                                "isHuman": True,
                            },
                            "chancellorCandidate": {
                                "id": nominee.id,
                                "name": getattr(
                                    nominee, "name", f"Player {nominee.id}"
                                ),
                            },
                        },
                        "newPhase": "voting",
                        "eligibleVoters": _get_eligible_voters(game),
                    }
                ),
                200,
            )

        else:
            nomination_result = nominate_chancellor_safe(game)

            if nomination_result["game_over"]:
                return (
                    jsonify(
                        {
                            "message": "Game ended during nomination",
                            "gameOver": True,
                            "winner": nomination_result["winner"],
                            "newPhase": "game_over",
                        }
                    ),
                    200,
                )

            if nomination_result["chaos_triggered"]:
                return (
                    jsonify(
                        {
                            "message": "No eligible chancellors - chaos policy enacted",
                            "chaosTriggered": True,
                            "newPhase": "election",
                        }
                    ),
                    200,
                )

            if nomination_result["nominee"]:
                game.state.current_phase_name = "voting"

                return (
                    jsonify(
                        {
                            "message": f"Bot president nominated chancellor - ready for human voting",
                            "nomination": {
                                "president": {
                                    "id": current_president.id,
                                    "name": getattr(
                                        current_president,
                                        "name",
                                        f"Bot {current_president.id}",
                                    ),
                                    "isBot": True,
                                    "strategy": getattr(
                                        current_president, "strategy_type", "unknown"
                                    ),
                                },
                                "chancellorCandidate": {
                                    "id": nomination_result["nominee"].id,
                                    "name": getattr(
                                        nomination_result["nominee"],
                                        "name",
                                        f'Player {nomination_result["nominee"].id}',
                                    ),
                                },
                            },
                            "newPhase": "voting",
                            "eligibleVoters": _get_eligible_voters(game),
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"error": "Bot nomination failed unexpectedly"}), 500

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to nominate chancellor: {str(e)}"}), 500


@app.route("/games/<game_id>/state", methods=["GET"])
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


@app.route("/games/<game_id>/add-bots", methods=["POST"])
def add_bots(game_id):
    """Agregar múltiples bots a la sala de juego.

    Request JSON:
        count (int): Número de bots a agregar
        strategy (str, optional): Estrategia para todos los bots (default: "smart")
        namePrefix (str, optional): Prefijo para nombres de bots (default: "Bot")
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

    for i in range(bot_count):
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


@app.route("/games/<game_id>/vote", methods=["POST"])
def cast_vote(game_id):
    """
    Handles the voting process for a given game round.
    This endpoint receives a vote from a player (human or AI) for the current election phase in the game.
    It validates the game state, ensures the player is eligible to vote, records the vote, and, if all votes
    are collected, resolves the election using the election_utils module.
    Args:
        game_id (str or int): The unique identifier of the game.
    Request JSON Body:
        vote (str): The vote value, either "ja" or "nein" (required for human players).
        playerId (str or int): The unique identifier of the player casting the vote.
    Returns:
        Response: A Flask JSON response with:
            - Success: Confirmation of vote, voting status, and election result if voting is complete.
            - Error: Appropriate error message and status code if voting is not allowed or fails.
    Possible Error Responses:
        400: Missing playerId or invalid vote value.
        403: Game not in progress, not in voting phase, or no nomination to vote on.
        404: Game or player not found.
        409: Player has already voted.
        500: Internal server error during voting process.
    Side Effects:
        - Records the player's vote in the game state.
        - Resolves the election and advances the game phase if all votes are collected.
        - Clears recorded votes after election resolution.
    """

    data = request.get_json() or {}
    vote = data.get("vote", "").lower()
    player_id = data.get("playerId")

    if player_id is None:
        return jsonify({"error": "Missing playerId"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    current_game_state = _get_game_state_status(game)
    current_phase = _get_current_phase_name(game)

    if current_game_state != "in_progress":
        return (
            jsonify(
                {
                    "error": "Game not in progress",
                    "currentGameState": current_game_state,
                    "currentPhase": current_phase,
                    "debug": {
                        "hasGameState": hasattr(game.state, "game_state"),
                        "gameStateValue": getattr(game.state, "game_state", "not_set"),
                        "hasPresident": hasattr(game.state, "president")
                        and game.state.president is not None,
                    },
                }
            ),
            403,
        )

    if (
        not hasattr(game.state, "chancellor_candidate")
        or not game.state.chancellor_candidate
    ):
        return (
            jsonify(
                {
                    "error": "No nomination to vote on",
                    "currentPhase": current_phase,
                    "hasChancellorCandidate": hasattr(
                        game.state, "chancellor_candidate"
                    ),
                    "chancellorCandidateValue": getattr(
                        game.state, "chancellor_candidate", None
                    ),
                }
            ),
            403,
        )

    if current_phase not in ["voting", "election"]:
        return (
            jsonify(
                {
                    "error": f"Not in voting phase",
                    "currentPhase": current_phase,
                    "expectedPhase": "voting",
                }
            ),
            403,
        )

    voting_player = None
    for player in game.state.players:
        if player.id == player_id:
            voting_player = player
            break

    if not voting_player:
        available_players = [
            {"id": p.id, "name": getattr(p, "name", f"Player {p.id}")}
            for p in game.state.players
        ]
        return (
            jsonify(
                {
                    "error": "Player not found",
                    "requestedPlayerId": player_id,
                    "availablePlayers": available_players,
                }
            ),
            404,
        )

    try:
        if not hasattr(game.state, "api_votes"):
            game.state.api_votes = {}

        if player_id in game.state.api_votes:
            return (
                jsonify(
                    {
                        "error": "Player has already voted",
                        "playerId": player_id,
                        "previousVote": (
                            "ja" if game.state.api_votes[player_id] else "nein"
                        ),
                    }
                ),
                409,
            )

        if getattr(voting_player, "player_type", "human") == "ai":
            ai_vote = voting_player.vote()
            game.state.api_votes[player_id] = ai_vote
            vote_display = "ja" if ai_vote else "nein"
            message = f"AI {getattr(voting_player, 'name', f'Bot_{player_id}')} voted '{vote_display}'"
        else:
            if vote not in ["ja", "nein"]:
                return jsonify({"error": "Vote must be 'ja' or 'nein'"}), 400

            vote_value = vote == "ja"
            game.state.api_votes[player_id] = vote_value
            vote_display = vote
            message = f"Human vote '{vote}' recorded"

        eligible_voter_count = len(
            [p for p in game.state.players if getattr(p, "is_alive", True)]
        )
        all_voted = len(game.state.api_votes) >= eligible_voter_count

        response_data = {
            "message": message,
            "votingComplete": all_voted,
            "playerVote": {
                "playerId": player_id,
                "playerName": getattr(voting_player, "name", f"Player {player_id}"),
                "vote": vote_display,
                "isAI": getattr(voting_player, "player_type", "human") == "ai",
            },
            "currentVoteCount": len(game.state.api_votes),
            "totalVotersNeeded": eligible_voter_count,
        }

        if all_voted:
            election_result = resolve_election(game, game.state.api_votes)

            response_data["electionResult"] = {
                "passed": election_result["passed"],
                "jaVotes": election_result["ja_votes"],
                "neinVotes": election_result["nein_votes"],
                "totalVotes": election_result["total_votes"],
            }

            response_data["newPhase"] = election_result["next_phase"]

            if election_result["game_over"]:
                response_data["gameOver"] = {
                    "winner": election_result["winner"],
                    "reason": "Game ended",
                }

            game.state.api_votes = {}
        else:
            response_data["newPhase"] = "voting"

        return jsonify(response_data), 200

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to cast vote: {str(e)}"}), 500


@app.route("/games/<game_id>/president/draw", methods=["POST"])
def president_draw_policies(game_id):
    """
    Handles the action where the president draws 3 policy cards during the legislative phase of the game.
    This function performs the following steps:
    - Validates that the game exists and is in progress.
    - Ensures the current phase is 'legislative' and both president and chancellor are assigned.
    - Checks that the president has not already drawn policies in this round.
    - Uses legislative_utils to draw 3 policies for the president.
    - If the president is a human player, returns the drawn policies and awaits a discard decision.
    - If the president is a bot, automatically discards a policy and proceeds to the chancellor's turn.
    - Returns appropriate JSON responses for each scenario, including error handling.
    Args:
        game_id (str or int): The unique identifier of the game.
    Returns:
        Response: A Flask JSON response with status code and relevant data or error message.
    """

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    current_game_state = _get_game_state_status(game)
    current_phase = _get_current_phase_name(game)

    if current_game_state != "in_progress":
        return (
            jsonify(
                {
                    "error": "Game not in progress",
                    "currentGameState": current_game_state,
                    "currentPhase": current_phase,
                }
            ),
            403,
        )

    if current_phase != "legislative":
        return (
            jsonify(
                {
                    "error": f"Not in legislative phase",
                    "currentPhase": current_phase,
                    "expectedPhase": "legislative",
                }
            ),
            403,
        )

    if not hasattr(game.state, "president") or not game.state.president:
        return jsonify({"error": "No president assigned"}), 403

    if not hasattr(game.state, "chancellor") or not game.state.chancellor:
        return jsonify({"error": "No chancellor assigned"}), 403

    if (
        hasattr(game.state, "presidential_policies")
        and game.state.presidential_policies
    ):
        return (
            jsonify(
                {
                    "error": "President has already drawn policies",
                    "currentSubPhase": "president_discard",
                }
            ),
            403,
        )

    try:
        draw_result = draw_presidential_policies(game)

        game.state.presidential_policies = draw_result["policies"]

        president = game.state.president
        president_is_human = getattr(president, "player_type", "human") == "human"

        if president_is_human:
            return (
                jsonify(
                    {
                        "message": "President drew 3 policies - awaiting discard choice",
                        "drawResult": {
                            "policyNames": draw_result["policy_names"],
                            "deckRemaining": draw_result["deck_remaining"],
                            "mustChoose": 2,
                            "mustDiscard": 1,
                        },
                        "president": {
                            "id": president.id,
                            "name": getattr(
                                president, "name", f"Player {president.id}"
                            ),
                            "isHuman": True,
                            "mustDiscard": True,
                        },
                        "gamePhase": "president_discard",
                        "newPhase": "legislative",
                        "subPhase": "president_discard",
                        "requiresHumanInput": True,
                        "availableActions": ["discard_policy"],
                    }
                ),
                200,
            )

        else:
            chosen, discarded = game.presidential_policy_choice(draw_result["policies"])

            policy_indices = []
            for i, policy in enumerate(draw_result["policies"]):
                if policy in chosen:
                    policy_indices.append(i)

            choice_result = handle_presidential_choice(game, policy_indices)

            if not choice_result["success"]:
                return (
                    jsonify(
                        {
                            "error": "Failed to process bot president choice",
                            "details": choice_result,
                        }
                    ),
                    500,
                )

            return (
                jsonify(
                    {
                        "message": "Bot president automatically drew and discarded policy",
                        "drawResult": {
                            "policyNames": draw_result["policy_names"],
                            "deckRemaining": draw_result["deck_remaining"],
                        },
                        "presidentialChoice": {
                            "chosenPolicies": choice_result["chosen_names"],
                            "discardedPolicy": choice_result["discarded_name"],
                            "automatic": True,
                        },
                        "president": {
                            "id": president.id,
                            "name": getattr(president, "name", f"Bot {president.id}"),
                            "isBot": True,
                            "strategy": getattr(president, "strategy_type", "unknown"),
                        },
                        "chancellor": {
                            "id": game.state.chancellor.id,
                            "name": getattr(
                                game.state.chancellor,
                                "name",
                                f"Player {game.state.chancellor.id}",
                            ),
                            "mustEnact": True,
                        },
                        "gamePhase": "chancellor_enact",
                        "newPhase": "legislative",
                        "subPhase": "chancellor_enact",
                        "availableActions": (
                            ["enact_policy"]
                            if getattr(game.state.chancellor, "player_type", "human")
                            == "human"
                            else []
                        ),
                    }
                ),
                200,
            )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to draw policies: {str(e)}"}), 500


@app.route("/games/<game_id>/president/discard", methods=["POST"])
def president_discard_policy(game_id):
    """
    Handles the president's action of discarding one of the three legislative policies in a Secret Hitler-like game.
    Args:
        game_id (str or int): The unique identifier for the game session.
    Request JSON Body:
        discardIndex (int): The index (0, 1, or 2) of the policy to discard.
    Returns:
        Response: A Flask JSON response with:
            - 200 OK and details of the discarded policy and next phase if successful.
            - 400 Bad Request if required data is missing or invalid.
            - 403 Forbidden if the game state does not allow discarding.
            - 404 Not Found if the game does not exist.
            - 500 Internal Server Error for unexpected failures.
    Side Effects:
        - Updates the game state by discarding the selected policy.
        - Advances the game to the chancellor's enactment phase if successful.
    Raises:
        Exception: Returns a 500 error with details if an unexpected error occurs.
    """

    data = request.get_json() or {}
    discard_index = data.get("discardIndex")

    if discard_index is None:
        return jsonify({"error": "Missing discardIndex (0, 1, or 2)"}), 400

    if discard_index not in [0, 1, 2]:
        return jsonify({"error": "discardIndex must be 0, 1, or 2"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if (
        not hasattr(game.state, "presidential_policies")
        or not game.state.presidential_policies
    ):
        return (
            jsonify(
                {
                    "error": "No presidential policies available to discard",
                    "suggestion": "Call /president/draw first",
                }
            ),
            403,
        )

    if len(game.state.presidential_policies) != 3:
        return (
            jsonify(
                {
                    "error": "President must have exactly 3 policies to discard",
                    "currentPolicies": len(game.state.presidential_policies),
                }
            ),
            403,
        )

    try:
        keep_indices = [i for i in range(3) if i != discard_index]

        choice_result = handle_presidential_choice(game, keep_indices)

        if not choice_result["success"]:
            return (
                jsonify(
                    {
                        "error": "Failed to process presidential choice",
                        "details": choice_result,
                    }
                ),
                500,
            )

        return (
            jsonify(
                {
                    "message": "President discarded policy successfully",
                    "presidentialChoice": {
                        "chosenPolicies": choice_result["chosen_names"],
                        "discardedPolicy": choice_result["discarded_name"],
                        "discardIndex": discard_index,
                    },
                    "chancellor": {
                        "id": game.state.chancellor.id,
                        "name": getattr(
                            game.state.chancellor,
                            "name",
                            f"Player {game.state.chancellor.id}",
                        ),
                        "mustEnact": True,
                        "isHuman": getattr(
                            game.state.chancellor, "player_type", "human"
                        )
                        == "human",
                    },
                    "gamePhase": "chancellor_enact",
                    "newPhase": "legislative",
                    "subPhase": "chancellor_enact",
                    "availableActions": (
                        ["enact_policy"]
                        if getattr(game.state.chancellor, "player_type", "human")
                        == "human"
                        else []
                    ),
                }
            ),
            200,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to discard policy: {str(e)}"}), 500


@app.route("/games/<game_id>/chancellor/enact", methods=["POST"])
def chancellor_enact_policy(game_id):
    """
    Allows the chancellor to enact one of the two legislative policies in a Secret Hitler-like game.
    This endpoint handles both human and bot chancellors, performing all necessary validations and state transitions.
    It uses granular control utilities to process the chancellor's choice, update the game state, and determine the next phase.
    Args:
        game_id (str or int): The unique identifier of the game session.
    Request JSON Body:
        enactIndex (int): Index (0 or 1) indicating which policy the chancellor chooses to enact.
    Returns:
        Response: A Flask JSON response with:
            - Success or error message.
            - Details of the enacted and discarded policies.
            - Information about the chancellor (human or bot).
            - Policy result and any executive power granted.
            - Game over status and winner if applicable.
            - Next phase and available actions.
    Errors:
        400: Missing or invalid enactIndex.
        403: Game not in progress, wrong phase, no chancellor assigned, or invalid policy state.
        404: Game not found.
        500: Internal error processing the chancellor's choice.
    Notes:
        - For human chancellors, waits for manual input and provides detailed feedback.
        - For bot chancellors, automatically selects and enacts a policy, and may execute executive powers if the president is also a bot.
        - Handles all state transitions, including ending the legislative session, granting executive powers, and determining game over conditions.
    """

    data = request.get_json() or {}
    enact_index = data.get("enactIndex")

    if enact_index is None:
        return jsonify({"error": "Missing enactIndex (0 or 1)"}), 400

    if enact_index not in [0, 1]:
        return jsonify({"error": "enactIndex must be 0 or 1"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    current_game_state = _get_game_state_status(game)
    current_phase = _get_current_phase_name(game)

    if current_game_state != "in_progress":
        return (
            jsonify(
                {
                    "error": "Game not in progress",
                    "currentGameState": current_game_state,
                    "currentPhase": current_phase,
                }
            ),
            403,
        )

    if current_phase != "legislative":
        return (
            jsonify(
                {
                    "error": f"Not in legislative phase",
                    "currentPhase": current_phase,
                    "expectedPhase": "legislative",
                }
            ),
            403,
        )

    if not hasattr(game.state, "chancellor") or not game.state.chancellor:
        return jsonify({"error": "No chancellor assigned"}), 403

    if (
        not hasattr(game.state, "chancellor_policies")
        or not game.state.chancellor_policies
    ):
        return (
            jsonify(
                {
                    "error": "No chancellor policies available to enact",
                    "suggestion": "President must draw and discard first",
                    "currentSubPhase": "awaiting_president_discard",
                }
            ),
            403,
        )

    if len(game.state.chancellor_policies) != 2:
        return (
            jsonify(
                {
                    "error": "Chancellor must have exactly 2 policies to choose from",
                    "currentPolicies": len(game.state.chancellor_policies),
                }
            ),
            403,
        )

    try:
        chancellor = game.state.chancellor
        chancellor_is_human = getattr(chancellor, "player_type", "human") == "human"

        if chancellor_is_human:
            choice_result = handle_chancellor_choice(game, enact_index)

            if not choice_result["success"]:
                return (
                    jsonify(
                        {
                            "error": "Failed to process chancellor choice",
                            "details": choice_result,
                        }
                    ),
                    500,
                )

            response_data = {
                "message": "Policy enacted successfully by human chancellor",
                "chancellorChoice": {
                    "enactedPolicy": choice_result["enacted_name"],
                    "discardedPolicy": choice_result["discarded_name"],
                    "enactIndex": enact_index,
                },
                "policyResult": {
                    "enacted": choice_result["enacted_name"],
                    "powerGranted": choice_result["power_granted"],
                },
                "chancellor": {
                    "id": chancellor.id,
                    "name": getattr(chancellor, "name", f"Player {chancellor.id}"),
                    "isHuman": True,
                },
                "gameOver": choice_result["game_over"],
                "winner": (
                    choice_result["winner"] if choice_result["game_over"] else None
                ),
            }

            if choice_result["game_over"]:
                response_data["newPhase"] = "game_over"
                response_data["gameOver"] = {
                    "winner": choice_result["winner"],
                    "reason": "Policy victory",
                }
            elif choice_result["power_granted"]:
                response_data["newPhase"] = "executive_power"
                response_data["subPhase"] = "executive_power"
                response_data["executivePower"] = {
                    "powerType": choice_result["power_granted"],
                    "president": {
                        "id": game.state.president.id,
                        "name": getattr(
                            game.state.president,
                            "name",
                            f"Player {game.state.president.id}",
                        ),
                        "mustExecutePower": True,
                    },
                }
                response_data["availableActions"] = ["execute_power"]
            else:
                session_end = end_legislative_session(game)
                response_data["sessionEnd"] = session_end
                response_data["newPhase"] = "election"
                response_data["subPhase"] = "nomination"
                response_data["nextPresident"] = (
                    {
                        "id": game.state.president.id,
                        "name": getattr(
                            game.state.president,
                            "name",
                            f"Player {game.state.president.id}",
                        ),
                    }
                    if hasattr(game.state, "president") and game.state.president
                    else None
                )

            return jsonify(response_data), 200

        else:
            enacted, discarded = game.chancellor_policy_choice(
                game.state.chancellor_policies
            )

            auto_enact_index = 0 if game.state.chancellor_policies[0] == enacted else 1

            choice_result = handle_chancellor_choice(game, auto_enact_index)

            if not choice_result["success"]:
                return (
                    jsonify(
                        {
                            "error": "Failed to process bot chancellor choice",
                            "details": choice_result,
                        }
                    ),
                    500,
                )

            response_data = {
                "message": "Bot chancellor automatically enacted policy",
                "chancellorChoice": {
                    "enactedPolicy": choice_result["enacted_name"],
                    "discardedPolicy": choice_result["discarded_name"],
                    "enactIndex": auto_enact_index,
                    "automatic": True,
                },
                "policyResult": {
                    "enacted": choice_result["enacted_name"],
                    "powerGranted": choice_result["power_granted"],
                },
                "chancellor": {
                    "id": chancellor.id,
                    "name": getattr(chancellor, "name", f"Bot {chancellor.id}"),
                    "isBot": True,
                    "strategy": getattr(chancellor, "strategy_type", "unknown"),
                },
                "gameOver": choice_result["game_over"],
                "winner": (
                    choice_result["winner"] if choice_result["game_over"] else None
                ),
            }

            if choice_result["game_over"]:
                response_data["newPhase"] = "game_over"
                response_data["gameOver"] = {
                    "winner": choice_result["winner"],
                    "reason": "Policy victory",
                }
            elif choice_result["power_granted"]:
                if getattr(game.state.president, "player_type", "human") == "ai":
                    power_result = execute_presidential_power(
                        game, choice_result["power_granted"]
                    )

                    if power_result.get("success", False):
                        response_data["powerExecution"] = power_result

                        if power_result.get("game_over", False):
                            response_data["newPhase"] = "game_over"
                            response_data["gameOver"] = {
                                "winner": power_result["winner"],
                                "reason": (
                                    "Hitler executed"
                                    if power_result.get("hitler_executed")
                                    else "Game ended"
                                ),
                            }
                        else:
                            session_end = end_legislative_session(game)
                            response_data["sessionEnd"] = session_end
                            response_data["newPhase"] = "election"
                    else:
                        response_data["powerExecutionError"] = power_result
                        response_data["newPhase"] = "executive_power"
                else:
                    response_data["newPhase"] = "executive_power"
                    response_data["executivePower"] = {
                        "powerType": choice_result["power_granted"],
                        "president": {
                            "id": game.state.president.id,
                            "name": getattr(
                                game.state.president,
                                "name",
                                f"Player {game.state.president.id}",
                            ),
                            "isHuman": True,
                            "mustExecutePower": True,
                        },
                    }
            else:
                session_end = end_legislative_session(game)
                response_data["sessionEnd"] = session_end
                response_data["newPhase"] = "election"
                response_data["subPhase"] = "nomination"
                response_data["nextPresident"] = (
                    {
                        "id": game.state.president.id,
                        "name": getattr(
                            game.state.president,
                            "name",
                            f"Player {game.state.president.id}",
                        ),
                    }
                    if hasattr(game.state, "president") and game.state.president
                    else None
                )

            return jsonify(response_data), 200

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to enact policy: {str(e)}"}), 500


@app.route("/games/<game_id>/president/execute-power", methods=["POST"])
def execute_presidential_power_endpoint(game_id):
    """
    Endpoint to execute a presidential power in the game.
    This endpoint allows the current president to use their executive power during the "executive_power" phase.
    It validates the game state, ensures the requesting player is the president, and executes the specified power.
    If the power results in the game ending, the response includes game over information.
    Otherwise, it ends the legislative session and transitions the game to the next phase.
    Args:
        game_id (str): The unique identifier of the game.
    Request JSON Body:
        powerType (str): The type of presidential power to execute.
        playerId (str): The ID of the president executing the power.
        targetId (str, optional): The ID of the target player, if applicable.
    Returns:
        Response: A Flask JSON response with the result of the power execution, including error messages,
        game state updates, and phase transitions.
        - 200: Power executed successfully.
        - 400: Failed to execute power due to invalid input or game state.
        - 403: Not authorized or not in the correct phase.
        - 404: Game not found.
        - 500: Internal server error.
    """
    data = request.get_json() or {}
    power_type = data.get("powerType")
    player_id = data.get("playerId")
    target_id = data.get("targetId")

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    current_phase = _get_current_phase_name(game)
    if current_phase != "executive_power":
        return (
            jsonify(
                {
                    "error": f"Not in executive power phase",
                    "currentPhase": current_phase,
                }
            ),
            403,
        )

    if not game.state.president or game.state.president.id != player_id:
        return jsonify({"error": "Only the president can execute powers"}), 403

    try:
        power_result = execute_presidential_power(
            game=game, power_type=power_type, target_player_id=target_id
        )

        if not power_result.get("success", True):
            return (
                jsonify(
                    {
                        "error": "Failed to execute power",
                        "details": power_result.get("error"),
                    }
                ),
                400,
            )

        response_data = {
            "message": f"President executed power: {power_type}",
            "powerResult": power_result,
            "president": {
                "id": game.state.president.id,
                "name": getattr(
                    game.state.president, "name", f"Player {game.state.president.id}"
                ),
            },
        }

        if power_result.get("game_over", False):
            response_data["gameOver"] = True
            response_data["winner"] = power_result.get("winner")
            response_data["newPhase"] = "game_over"
            return jsonify(response_data), 200

        session_end = end_legislative_session(game)
        response_data["sessionEnd"] = session_end
        response_data["newPhase"] = "election"
        response_data["subPhase"] = "nomination"

        return jsonify(response_data), 200

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to execute power: {str(e)}"}), 500


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


def _get_power_description(power_name):
    """
    Returns a human-readable description for a given power name.

    Args:
        power_name (str): The key representing the name of the power.

    Returns:
        str: A description of the specified power. If the power name is not found,
             returns a default message indicating execution of the given power.
    """
    power_descriptions = {
        "investigate_loyalty": "Investigate a player's loyalty",
        "special_election": "Call a special election",
        "policy_peek": "Peek at the top 3 policies",
        "execution": "Execute a player",
        "confession": "President reveals their party",
        "bugging": "Investigate a player (Communist power)",
        "five_year_plan": "Add policies to deck",
        "congress": "View and choose policies",
        "radicalization": "Convert a player to communist",
        "propaganda": "View top policy and optionally discard",
        "impeachment": "Reveal party membership",
    }
    return power_descriptions.get(power_name, f"Execute {power_name} power")


def _get_current_phase_name(game):
    """
    Returns the name of the current phase of the game.
    This function attempts to determine the current phase name by checking several possible sources in order:
    1. If `game.state` has a non-empty `current_phase_name` attribute, it is returned.
    2. If `game` has a non-empty `current_phase` attribute, its class name (with 'Phase' removed and lowercased) is used as the phase name. This value is also set to `game.state.current_phase_name` if possible.
    3. If neither of the above is available, the phase name is inferred using `_infer_phase_from_game_state(game)`.
    Args:
        game: The game object containing state and phase information.
    Returns:
        str: The name of the current phase.
    """

    if hasattr(game.state, "current_phase_name") and game.state.current_phase_name:
        return game.state.current_phase_name

    if hasattr(game, "current_phase") and game.current_phase:
        backend_phase_name = game.current_phase.__class__.__name__.lower().replace(
            "phase", ""
        )
        if hasattr(game.state, "current_phase_name"):
            game.state.current_phase_name = backend_phase_name
        return backend_phase_name

    return _infer_phase_from_game_state(game)


def _infer_phase_from_game_state(game):
    """
    Infers the current phase of the game based on the attributes of the game state.

    Parameters:
        game: An object representing the current game, expected to have a 'state' attribute
              with various properties indicating the game's progress.

    Returns:
        str: A string representing the inferred phase of the game. Possible values are:
            - "game_over": The game has ended.
            - "voting": The game is in the voting phase for a chancellor candidate.
            - "legislative": Both president and chancellor are set, indicating the legislative phase.
            - "election": Only the president is set, indicating the election phase.
            - "setup": The game is in the setup phase or no other phase matches.
    """
    if hasattr(game.state, "game_over") and game.state.game_over:
        return "game_over"
    elif (
        hasattr(game.state, "chancellor_candidate") and game.state.chancellor_candidate
    ):
        return "voting"
    elif (
        hasattr(game.state, "president")
        and game.state.president
        and hasattr(game.state, "chancellor")
        and game.state.chancellor
    ):
        return "legislative"
    elif hasattr(game.state, "president") and game.state.president:
        return "election"
    else:
        return "setup"


def _get_eligible_voters(game):
    """
    Returns a list of eligible voters from the current game state.
    Each eligible voter is represented as a dictionary containing:
        - "id": The player's unique identifier.
        - "name": The player's name (defaults to 'Player {id}' if not set).
        - "hasVoted": Boolean indicating if the player has already voted.
        - "vote": Always set to None to avoid revealing votes before the end.
    A player is considered eligible if their 'is_alive' attribute is True (or defaults to True if not present).
    Args:
        game: The game object containing the current state and players.
    Returns:
        List[dict]: A list of dictionaries, each representing an eligible voter.
    """
    eligible_voters = []

    for player in game.state.players:
        is_alive = getattr(player, "is_alive", True)

        if is_alive:
            eligible_voters.append(
                {
                    "id": player.id,
                    "name": getattr(player, "name", f"Player {player.id}"),
                    "hasVoted": player.id in getattr(game.state, "votes", {}),
                    "vote": None,
                }
            )

    return eligible_voters


def _get_game_config_info(game):
    """
    Retrieve the configuration settings of a game object.

    Args:
        game: An object representing the game, expected to have configuration attributes.

    Returns:
        dict: A dictionary containing the following game configuration options:
            - maxPlayers (int): Maximum number of players (default: 10).
            - withCommunists (bool): Whether communists are included (default: False).
            - withAntiPolicies (bool): Whether anti-policies are enabled (default: False).
            - withEmergencyPowers (bool): Whether emergency powers are enabled (default: False).
            - aiStrategy (str): The AI strategy to use (default: 'smart').
    """
    return {
        "maxPlayers": getattr(game, "player_count", 10),
        "withCommunists": getattr(game, "include_communists", False),
        "withAntiPolicies": getattr(game, "with_anti_policies", False),
        "withEmergencyPowers": getattr(game, "with_emergency_powers", False),
        "aiStrategy": getattr(game, "ai_strategy", "smart"),
    }


def _can_see_role(game, player, requesting_player_id):
    """
    Determines if the role of a player can be viewed by the requesting player according to game rules.
    Args:
        game: The current game instance containing the state and rules.
        player: The player whose role visibility is being checked.
        requesting_player_id: The ID of the player requesting to see the role, or None.
    Returns:
        bool: True if the requesting player can see the role, False otherwise.
    Rules:
        - A player can always see their own role.
        - All roles become visible when the game is over.
    """
    if requesting_player_id is not None and player.id == requesting_player_id:
        return True

    if hasattr(game.state, "game_over") and game.state.game_over:
        return True

    return False


def _get_player_special_status(game, player):
    """
    Returns a list of special status strings for a given player in the current game state.
    Checks the EnhancedGameState attributes to determine if the player is:
    - "term_limited": The player is in the list of term-limited players.
    - "investigated": The player is in the list of investigated players.
    - "marked_for_execution": The player is marked for execution.
    Args:
        game: The game object containing the current state.
        player: The player object or identifier to check.
    Returns:
        list: A list of status strings representing the player's special statuses.
    """
    status = []

    if (
        hasattr(game.state, "term_limited_players")
        and player in game.state.term_limited_players
    ):
        status.append("term_limited")

    if (
        hasattr(game.state, "investigated_players")
        and player in game.state.investigated_players
    ):
        status.append("investigated")

    if (
        hasattr(game.state, "marked_for_execution")
        and game.state.marked_for_execution == player
    ):
        status.append("marked_for_execution")

    return status


def _get_current_timestamp():
    """
    Returns the current timestamp as an ISO 8601 formatted string.

    Returns:
        str: The current date and time in ISO 8601 format.
    """
    import datetime

    return datetime.datetime.now().isoformat()


def _get_game_state_status(game):
    """Determinar el estado actual del juego."""
    if hasattr(game.state, "game_over") and game.state.game_over:
        return "game_over"
    elif hasattr(game.state, "president") and game.state.president:
        return "in_progress"
    else:
        return "waiting_for_players"


def _get_current_phase_info(game):
    """
    Retrieve information about the current phase of the game.
    Args:
        game: An object representing the current game state. It is expected to have a 'state' attribute
              with at least a 'current_phase_name' property, and possibly other phase-specific attributes.
    Returns:
        dict: A dictionary containing details about the current phase, including:
            - 'name': The internal name of the phase.
            - 'displayName': A user-friendly display name for the phase.
            - 'description': A description of the phase.
            - 'originalClass': The original class name for the phase.
            - 'canAdvance': Boolean indicating if the phase can be advanced.
            - 'subPhase' (optional): The current sub-phase, if applicable (e.g., 'voting', 'nomination', etc.).
    Notes:
        The function determines the sub-phase for 'election' and 'legislative' phases based on the presence
        and state of specific attributes in the game state.
    """

    phase_name = getattr(game.state, "current_phase_name", "unknown")

    api_phase = {
        "name": phase_name,
        "displayName": _get_phase_display_name(phase_name),
        "description": _get_phase_description(game, phase_name),
        "originalClass": f"{phase_name.title()}Phase",
        "canAdvance": True,
    }

    if phase_name == "election":
        if (
            hasattr(game.state, "chancellor_candidate")
            and game.state.chancellor_candidate
        ):
            api_phase["subPhase"] = "voting"
        else:
            api_phase["subPhase"] = "nomination"
    elif phase_name == "legislative":
        if (
            hasattr(game.state, "chancellor_policies")
            and game.state.chancellor_policies
        ):
            api_phase["subPhase"] = "chancellor_enact"
        elif (
            hasattr(game.state, "president_policies") and game.state.president_policies
        ):
            api_phase["subPhase"] = "president_discard"
        else:
            api_phase["subPhase"] = "draw_policies"

    return api_phase


def _get_phase_display_name(phase_name):
    """
    Returns the display name for a given phase.

    Args:
        phase_name (str): The internal name of the phase.

    Returns:
        str: The display name in Spanish for the phase if it exists in the mapping,
             otherwise returns the title-cased version of the input phase name.
    """
    names = {
        "setup": "Configuración",
        "election": "Elección",
        "legislative": "Legislativa",
        "game_over": "Juego Terminado",
    }
    return names.get(phase_name, phase_name.title())


def _get_phase_description(game, phase_name):
    """
    Returns a human-readable description for the current phase of the game.

    Args:
        game: The game object containing the current state.
        phase_name (str): The name of the current phase.

    Returns:
        str: A description of the current phase, or a formatted string for unknown phases.

    Phases:
        - "setup": Returns "Configurando el juego".
        - "election": Returns "Nominar y votar canciller".
        - "legislative": Returns "Seleccionar y promulgar políticas".
        - "game_over": Returns "Juego terminado - Ganador: <winner>".
        - Any other phase: Returns "Fase: <phase_name>".
    """
    if phase_name == "setup":
        return "Configurando el juego"
    elif phase_name == "election":
        return "Nominar y votar canciller"
    elif phase_name == "legislative":
        return "Seleccionar y promulgar políticas"
    elif phase_name == "game_over":
        winner = getattr(game.state, "winner", "unknown")
        winner_str = _safe_winner_string(winner)
        return f"Juego terminado - Ganador: {winner_str.title()}"
    else:
        return f"Fase: {phase_name}"


def _get_players_info(game, requesting_player_id=None):
    """
    Retrieve detailed information about all players in the game.
    This function compiles a list of dictionaries, each containing information about a player,
    such as their ID, name, alive status, type (human or bot), position, role visibility, and any special status.
    Role information is included only if the requesting player is allowed to see it, as determined by `_can_see_role`.
    Args:
        game: The game instance containing the current state and players.
        requesting_player_id (optional): The ID of the player requesting the information, used to determine role visibility.
    Returns:
        list: A list of dictionaries, each representing a player's information, including role details if visible.
    """
    if not hasattr(game.state, "players") or not game.state.players:
        return []

    players_info = []

    for player in game.state.players:
        player_info = {
            "id": player.id,
            "name": getattr(player, "name", f"Player {player.id}"),
            "isAlive": not getattr(player, "is_dead", False),
            "isHuman": getattr(player, "player_type", "human") == "human",
            "isBot": getattr(player, "player_type", "human") == "ai",
            "position": player.id,
        }

        if _can_see_role(game, player, requesting_player_id):
            if hasattr(player, "role") and player.role:
                player_info["role"] = {
                    "party": getattr(player.role, "party_membership", "Unknown"),
                    "isHitler": getattr(player.role, "is_hitler", False),
                    "isFascist": getattr(player.role, "party_membership", "")
                    == "fascist",
                    "isLiberal": getattr(player.role, "party_membership", "")
                    == "liberal",
                    "isCommunist": getattr(player.role, "party_membership", "")
                    == "communist",
                    "isVisible": True,
                }
            else:
                player_info["role"] = {"isVisible": False}
        else:
            player_info["role"] = {"isVisible": False}

        player_info["specialStatus"] = _get_player_special_status(game, player)

        players_info.append(player_info)

    return players_info


def _get_government_info(game):
    """
    Retrieve structured information about the current and previous government state in the game.
    Args:
        game: An instance of the game containing the current state and player information.
    Returns:
        dict: A dictionary with the following keys:
            - "president": Information about the current president (id and name), or None if not set.
            - "chancellor": Information about the current chancellor (id and name), or None if not set.
            - "presidentCandidate": Information about the current president candidate (id and name), or None if not set.
            - "chancellorCandidate": Information about the current chancellor candidate (id and name), or None if not set.
            - "previousGovernment": A dictionary with the previous president and chancellor (id and name), or None if not set.
            - "termLimited": List of players who are currently term-limited.
    Notes:
        - Player names are retrieved from the player object if available; otherwise, a default name is generated.
        - Relies on helper functions such as _get_player_name_by_id and _get_term_limited_players.
    """
    government = {
        "president": None,
        "chancellor": None,
        "presidentCandidate": None,
        "chancellorCandidate": None,
        "previousGovernment": None,
    }

    if hasattr(game.state, "president") and game.state.president:
        government["president"] = {
            "id": game.state.president.id,
            "name": getattr(
                game.state.president, "name", f"Player {game.state.president.id}"
            ),
        }

    if hasattr(game.state, "chancellor") and game.state.chancellor:
        government["chancellor"] = {
            "id": game.state.chancellor.id,
            "name": getattr(
                game.state.chancellor, "name", f"Player {game.state.chancellor.id}"
            ),
        }

    if hasattr(game.state, "chancellor_candidate") and game.state.chancellor_candidate:
        candidate = game.state.chancellor_candidate
        government["chancellorCandidate"] = {
            "id": candidate.id,
            "name": getattr(candidate, "name", f"Player {candidate.id}"),
        }

    if hasattr(game.state, "previous_government") and game.state.previous_government:
        prev_gov = game.state.previous_government
        government["previousGovernment"] = {
            "president": {
                "id": prev_gov["president"],
                "name": _get_player_name_by_id(game, prev_gov["president"]),
            },
            "chancellor": {
                "id": prev_gov["chancellor"],
                "name": _get_player_name_by_id(game, prev_gov["chancellor"]),
            },
        }

    government["termLimited"] = _get_term_limited_players(game)

    return government


def _get_player_name_by_id(game, player_id):
    """
    Retrieve the name of a player given their ID.
    Args:
        game: An object containing the game state, which should have a 'players' attribute.
        player_id: The unique identifier of the player whose name is to be retrieved.
    Returns:
        str: The name of the player if found; otherwise, a default string in the format "Player {player_id}".
    """
    if not hasattr(game.state, "players") or not game.state.players:
        return f"Player {player_id}"

    for player in game.state.players:
        if player.id == player_id:
            return getattr(player, "name", f"Player {player_id}")

    return f"Player {player_id}"


def _get_term_limited_players(game):
    """
    Obtain a list of players who are restricted from being selected for government roles in the next round.
    Args:
        game: An object representing the current game state. It is expected to have a `state` attribute,
              which contains information about the previous government and the list of players.
    Returns:
        list of dict: A list of dictionaries, each representing a term-limited player with the following keys:
            - "id": The player's unique identifier.
            - "name": The player's name (or a default name if not available).
            - "reason": The reason for the term limit ("former_chancellor" or "former_president_small_game").
    Notes:
        - If there is no previous government, returns an empty list.
        - The former chancellor is always term-limited.
        - In games with 5 or fewer players, the former president is also term-limited.
    """
    term_limited = []

    if (
        not hasattr(game.state, "previous_government")
        or not game.state.previous_government
    ):
        return term_limited

    prev_gov = game.state.previous_government

    if not isinstance(prev_gov, dict):
        return term_limited

    prev_president_id = prev_gov.get("president")
    prev_chancellor_id = prev_gov.get("chancellor")

    if prev_president_id is None or prev_chancellor_id is None:
        return term_limited

    if prev_chancellor_id is not None:
        prev_chancellor = _get_player_by_id(game, prev_chancellor_id)
        if prev_chancellor:
            term_limited.append(
                {
                    "id": prev_chancellor_id,
                    "name": getattr(
                        prev_chancellor, "name", f"Player {prev_chancellor_id}"
                    ),
                    "reason": "former_chancellor",
                }
            )

    player_count = len(game.state.players) if hasattr(game.state, "players") else 0
    if player_count <= 5 and prev_president_id is not None:
        prev_president = _get_player_by_id(game, prev_president_id)
        if prev_president:
            term_limited.append(
                {
                    "id": prev_president_id,
                    "name": getattr(
                        prev_president, "name", f"Player {prev_president_id}"
                    ),
                    "reason": "former_president_small_game",
                }
            )

    return term_limited


def _get_player_by_id(game, player_id):
    """
    Retrieve a player object from the game's state by their unique player ID.
    Args:
        game: An object representing the current game, expected to have a 'state' attribute with a 'players' list.
        player_id: The unique identifier of the player to retrieve.
    Returns:
        The player object with the matching ID if found; otherwise, None.
    """
    if not hasattr(game.state, "players") or not game.state.players:
        return None

    for player in game.state.players:
        if player.id == player_id:
            return player

    return None


def _get_nomination_info(game):
    """
    Retrieve nomination information for the current game state.
    This function gathers details about the current nomination phase, including the eligible chancellor candidates,
    the current chancellor candidate (if any), and whether the game is in the voting phase. It uses the enhanced
    game state method `get_eligible_chancellors()` if available to determine eligible candidates.
    Args:
        game: The game instance containing the current state.
    Returns:
        dict: A dictionary with the following keys:
            - "chancellorCandidate": Information about the current chancellor candidate (dict or None).
            - "eligibleChancellors": List of eligible chancellor candidates, each as a dict with 'id', 'name', and 'isTermLimited'.
            - "isVotingPhase": Boolean indicating if the game is currently in the voting phase.
    """
    nomination = {
        "chancellorCandidate": None,
        "eligibleChancellors": [],
        "isVotingPhase": False,
    }

    if hasattr(game.state, "get_eligible_chancellors"):
        try:
            eligible = game.state.get_eligible_chancellors()
            nomination["eligibleChancellors"] = [
                {
                    "id": player.id,
                    "name": getattr(player, "name", f"Player {player.id}"),
                    "isTermLimited": player
                    in getattr(game.state, "term_limited_players", []),
                }
                for player in eligible
            ]
        except Exception as e:
            print(f"Warning: Could not get eligible chancellors: {e}")
            nomination["eligibleChancellors"] = []

    if hasattr(game.state, "chancellor_candidate") and game.state.chancellor_candidate:
        nomination["chancellorCandidate"] = {
            "id": game.state.chancellor_candidate.id,
            "name": getattr(
                game.state.chancellor_candidate,
                "name",
                f"Player {game.state.chancellor_candidate.id}",
            ),
        }
        nomination["isVotingPhase"] = True

    return nomination


def _get_trackers_info(game):
    """
    Extracts tracker information from the given game object.
    This function inspects the `game.state` object for specific tracker attributes
    and returns their values in a dictionary. If an attribute is not present,
    a default value is used.
    Args:
        game: An object representing the current game state, expected to have a `state` attribute.
    Returns:
        dict: A dictionary containing the following keys:
            - "electionTracker": The current value of the election tracker (default: 0).
            - "roundNumber": The current round number (default: 1).
            - "enactedPolicies": The list or count of enacted policies, if present.
    """
    trackers = {}

    if hasattr(game.state, "election_tracker"):
        trackers["electionTracker"] = game.state.election_tracker
    else:
        trackers["electionTracker"] = 0

    if hasattr(game.state, "round_number"):
        trackers["roundNumber"] = game.state.round_number
    else:
        trackers["roundNumber"] = 1

    if hasattr(game.state, "enacted_policies"):
        trackers["enactedPolicies"] = game.state.enacted_policies

    return trackers


def _get_board_info(game):
    """
    Retrieve the current state of the game board.
    This function extracts and returns information about the board's status, including the number of enacted policies for each faction, the number of policy cards in the deck and discard pile, whether the veto power is available, and the available powers for fascist and (optionally) communist factions.
    Args:
        game: The game instance containing the current state and board.
    Returns:
        dict: A dictionary with the following keys:
            - "liberalPolicies" (int): Number of liberal policies enacted.
            - "fascistPolicies" (int): Number of fascist policies enacted.
            - "communistPolicies" (int): Number of communist policies enacted.
            - "policiesInDeck" (int): Number of policy cards remaining in the deck.
            - "policiesInDiscard" (int): Number of policy cards in the discard pile.
            - "vetoAvailable" (bool): Whether the veto power is currently available.
            - "powers" (dict): Information about available powers for fascist and communist factions.
    """
    board_info = {
        "liberalPolicies": 0,
        "fascistPolicies": 0,
        "communistPolicies": 0,
        "policiesInDeck": 0,
        "policiesInDiscard": 0,
        "vetoAvailable": False,
    }

    if hasattr(game.state, "board") and game.state.board:
        board = game.state.board

        board_info["liberalPolicies"] = getattr(board, "liberal_track", 0)
        board_info["fascistPolicies"] = getattr(board, "fascist_track", 0)
        board_info["communistPolicies"] = getattr(board, "communist_track", 0)

        if hasattr(board, "policies"):
            board_info["policiesInDeck"] = len(board.policies) if board.policies else 0

        if hasattr(board, "discards"):
            board_info["policiesInDiscard"] = (
                len(board.discards) if board.discards else 0
            )

        board_info["vetoAvailable"] = getattr(board, "veto_available", False)

        board_info["powers"] = {
            "fascist": _get_fascist_powers_info(board),
            "communist": (
                _get_communist_powers_info(board)
                if getattr(game, "include_communists", False)
                else []
            ),
        }

    return board_info


def _get_fascist_powers_info(board):
    """
    Returns a list of dictionaries containing information about fascist powers on the given board.
    Each dictionary in the returned list includes:
        - position (int): The 1-based position of the power on the fascist track.
        - power (Any): The power at this position.
        - isActive (bool): Whether the power is currently active, based on the board's fascist track.
        - description (str): A textual description of the power, or "No power" if none.
    Args:
        board (object): The board object, expected to have 'fascist_powers' (iterable) and optionally 'fascist_track' (int).
    Returns:
        list[dict]: List of fascist power information dictionaries.
    """
    powers_info = []

    if hasattr(board, "fascist_powers") and board.fascist_powers:
        for i, power in enumerate(board.fascist_powers):
            position = i + 1
            is_active = getattr(board, "fascist_track", 0) >= position

            powers_info.append(
                {
                    "position": position,
                    "power": power,
                    "isActive": is_active,
                    "description": (
                        _get_power_description(power) if power else "No power"
                    ),
                }
            )

    return powers_info


def _get_communist_powers_info(board):
    """
    Gathers information about the communist powers present on the given board.
    Iterates through the `communist_powers` attribute of the board, if it exists, and constructs a list of dictionaries containing details for each power, including its position, name, activation status, and description.
    Args:
        board: An object representing the game board, expected to have `communist_powers` (list) and optionally `communist_track` (int) attributes.
    Returns:
        list[dict]: A list of dictionaries, each containing:
            - "position" (int): The 1-based index of the power.
            - "power" (Any): The power itself.
            - "isActive" (bool): Whether the power is currently active based on the board's communist track.
            - "description" (str): A description of the power, or "No power" if not present.
    """
    powers_info = []

    if hasattr(board, "communist_powers") and board.communist_powers:
        for i, power in enumerate(board.communist_powers):
            position = i + 1
            is_active = getattr(board, "communist_track", 0) >= position

            powers_info.append(
                {
                    "position": position,
                    "power": power,
                    "isActive": is_active,
                    "description": (
                        _get_power_description(power) if power else "No power"
                    ),
                }
            )

    return powers_info


def _get_last_action_info(game):
    """
    Infers and returns information about the last significant action in the game based on the current board state.
    The returned dictionary contains:
        - type (str): The type of the last action (e.g., 'policy_enacted', 'game_started', 'initialization', 'error').
        - player (dict or None): Information about the player involved in the last action, including 'id' and 'name', or None if not applicable.
        - description (str): A human-readable description of the last action.
        - timestamp (str): The timestamp when the action was inferred.
    The function attempts to:
        - Determine if a policy was enacted and by whom, using the previous government or current chancellor as fallback.
        - Identify the type of policy enacted (fascist, liberal, or communist).
        - Handle cases where the game has just started or is initializing.
        - Gracefully handle errors and return an error action if needed.
    Args:
        game: The game object containing the current state and board information.
    Returns:
        dict: A dictionary with details about the last action.
    """
    last_action = {"type": None, "player": None, "description": None, "timestamp": None}

    try:
        if hasattr(game.state, "board") and game.state.board:
            board = game.state.board

            liberal_count = getattr(board, "liberal_track", 0)
            fascist_count = getattr(board, "fascist_track", 0)
            communist_count = getattr(board, "communist_track", 0)
            total_policies = liberal_count + fascist_count + communist_count

            if total_policies > 0:
                last_chancellor = None

                if (
                    hasattr(game.state, "previous_government")
                    and game.state.previous_government
                ):
                    chancellor_id = game.state.previous_government.get("chancellor")
                    if chancellor_id is not None:
                        last_chancellor = {
                            "id": chancellor_id,
                            "name": _get_player_name_by_id(game, chancellor_id),
                        }

                if (
                    not last_chancellor
                    and hasattr(game.state, "chancellor")
                    and game.state.chancellor
                ):
                    last_chancellor = {
                        "id": game.state.chancellor.id,
                        "name": getattr(
                            game.state.chancellor,
                            "name",
                            f"Player {game.state.chancellor.id}",
                        ),
                    }

                if not last_chancellor:
                    last_chancellor = {"id": None, "name": "Unknown Chancellor"}

                if fascist_count > 0:
                    last_policy_type = "fascist"
                elif liberal_count > 0:
                    last_policy_type = "liberal"
                else:
                    last_policy_type = "communist"

                last_action = {
                    "type": "policy_enacted",
                    "player": last_chancellor,
                    "description": f"Policy #{total_policies} enacted: {last_policy_type.title()}",
                    "timestamp": _get_current_timestamp(),
                }
            else:
                last_action = {
                    "type": "game_started",
                    "player": {
                        "id": (
                            game.state.president.id
                            if hasattr(game.state, "president") and game.state.president
                            else 0
                        ),
                        "name": (
                            getattr(game.state.president, "name", "Unknown")
                            if hasattr(game.state, "president") and game.state.president
                            else "Host"
                        ),
                    },
                    "description": f"Game started - {len(game.state.players)} players",
                    "timestamp": _get_current_timestamp(),
                }
        else:
            last_action = {
                "type": "initialization",
                "player": None,
                "description": "Game initializing",
                "timestamp": _get_current_timestamp(),
            }

    except Exception as e:
        print(f"Error getting last action: {e}")
        last_action = {
            "type": "error",
            "player": None,
            "description": "Could not determine last action",
            "timestamp": _get_current_timestamp(),
        }

    return last_action


if __name__ == "__main__":
    """Punto de entrada principal del servidor.

    Inicia el servidor Flask en modo desarrollo con debug habilitado.
    El servidor escucha en 127.0.0.1:5000 por defecto.
    """
    app.run(host="127.0.0.1", port=5000, debug=True)
