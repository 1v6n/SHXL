"""Rutas de poderes ejecutivos.

Este módulo define las rutas de la API Flask para manejar la ejecución
de poderes presidenciales durante la fase ejecutiva del juego.
"""

from flask import Blueprint, jsonify, request
from src.game.phases.legislative_utils import (
    end_legislative_session,
    execute_presidential_power,
)

from ..storage import games
from ..utils.game_state_helpers import _get_current_phase_name

power_bp = Blueprint("power", __name__)


@power_bp.route("/games/<game_id>/president/execute-power", methods=["POST"])
def execute_presidential_power_endpoint(game_id):
    """Endpoint para ejecutar un poder presidencial en el juego.

    Este endpoint permite al presidente actual usar su poder ejecutivo durante
    la fase "executive_power". Valida el estado del juego, asegura que el jugador
    solicitante sea el presidente, y ejecuta el poder especificado.

    Args:
        game_id (str): Identificador único del juego.

    Returns:
        Response: Respuesta JSON de Flask con el resultado de la ejecución del poder.
            En caso de éxito (200):
            - message (str): Mensaje de confirmación
            - powerResult (dict): Resultado de la ejecución del poder
            - president (dict): Información del presidente
            - gameOver (bool, opcional): Si el juego terminó
            - sessionEnd (dict, opcional): Detalles del fin de sesión

            En caso de error (400/403/404/500):
            - error (str): Descripción del error

    Request JSON Body:
        powerType (str): Tipo de poder presidencial a ejecutar.
        playerId (str): ID del presidente ejecutando el poder.
        targetId (str, opcional): ID del jugador objetivo, si aplica.

    Note:
        Si el poder resulta en que el juego termine, la respuesta incluye
        información de fin de juego. De lo contrario, termina la sesión
        legislativa y transiciona el juego a la siguiente fase.
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
                    "error": "Not in executive power phase",
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
