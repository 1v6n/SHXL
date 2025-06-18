"""Rutas de la fase de elección.

Este módulo define las rutas de la API Flask para manejar las operaciones
de la fase de elección del juego, incluyendo nominación de canciller y votación.
"""

from flask import Blueprint, jsonify, request
from src.game.phases.election_utils import (
    check_marked_for_execution,
    nominate_chancellor_safe,
    resolve_election,
    run_full_election_cycle,
)

from ..storage import games
from ..utils.game_state_helpers import (
    _get_current_phase_name,
    _get_eligible_voters,
    _get_game_state_status,
)

election_bp = Blueprint("election", __name__)


@election_bp.route("/games/<game_id>/nominate", methods=["POST"])
def nominate_chancellor(game_id):
    """Maneja la fase de nominación de canciller en el juego.

    Esta función gestiona el proceso de nominar un canciller, soportando tanto
    jugadores humanos como IA. Realiza los siguientes pasos:
    1. Verifica ejecuciones pendientes antes de proceder con la nominación.
    2. Determina si todos los jugadores son bots; si es así, ejecuta el ciclo
       completo de elección automáticamente.
    3. Si hay al menos un humano presente, procede a votación individual.
    4. Maneja casos especiales como fin de juego o caos (sin cancilleres elegibles).

    Args:
        game_id (str): Identificador único del juego.

    Returns:
        Response: Respuesta JSON de Flask con el resultado de la fase de nominación,
            incluyendo mensajes de estado, detalles de nominación, votantes elegibles
            y transiciones de fase. Retorna códigos de estado HTTP apropiados para
            errores y éxito.

    Note:
        - Si el presidente es humano, espera nomineeId en la petición y valida elegibilidad.
        - Si el presidente es bot, nomina automáticamente pero requiere votación humana.
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
                            "message": "Bot president nominated chancellor - ready for human voting",
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


@election_bp.route("/games/<game_id>/vote", methods=["POST"])
def cast_vote(game_id):
    """Maneja el proceso de votación para una ronda de juego dada.

    Este endpoint recibe un voto de un jugador (humano o IA) para la fase de
    elección actual en el juego. Valida el estado del juego, asegura que el
    jugador sea elegible para votar, registra el voto y, si se recopilan todos
    los votos, resuelve la elección usando el módulo election_utils.

    Args:
        game_id (str): Identificador único del juego.

    Request JSON Body:
        vote (str): Valor del voto, "ja" o "nein" (requerido para jugadores humanos).
        playerId (str): Identificador único del jugador que emite el voto.

    Returns:
        Response: Respuesta JSON de Flask con confirmación de voto, estado de
            votación y resultado de elección si la votación está completa.

    Note:
        Posibles respuestas de error:
        - 400: playerId faltante o valor de voto inválido.
        - 403: Juego no en progreso, no en fase de votación, o sin nominación.
        - 404: Juego o jugador no encontrado.
        - 409: Jugador ya ha votado.
        - 500: Error interno del servidor durante el proceso de votación.

        Efectos secundarios:
        - Registra el voto del jugador en el estado del juego.
        - Resuelve la elección y avanza la fase si se recopilan todos los votos.
        - Limpia votos registrados después de resolución de elección.
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
                    "error": "Not in voting phase",
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
