"""
Executive power routes
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
