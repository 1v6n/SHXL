"""Rutas de la fase legislativa.

Este módulo define las rutas de la API Flask para manejar las operaciones
de la fase legislativa del juego, incluyendo robo de políticas, descarte
presidencial, promulgación de canciller y ejecución de poderes.
"""

from flask import Blueprint, jsonify, request

from src.game.phases.legislative_utils import (
    draw_presidential_policies,
    end_legislative_session,
    execute_presidential_power,
    handle_chancellor_choice,
    handle_presidential_choice,
)

from ..storage import games
from ..utils.game_state_helpers import _get_current_phase_name, _get_game_state_status

legislative_bp = Blueprint("legislative", __name__)


@legislative_bp.route("/games/<game_id>/president/draw", methods=["POST"])
def president_draw_policies(game_id):
    """Maneja la acción donde el presidente roba 3 cartas de política durante la fase legislativa.

    Esta función realiza los siguientes pasos:
    - Valida que el juego exista y esté en progreso.
    - Asegura que la fase actual sea 'legislative' y que presidente y canciller estén asignados.
    - Verifica que el presidente no haya robado políticas ya en esta ronda.
    - Usa legislative_utils para robar 3 políticas para el presidente.
    - Si el presidente es humano, retorna las políticas robadas y espera decisión de descarte.
    - Si el presidente es bot, automáticamente descarta una política y procede al turno del canciller.

    Args:
        game_id (str): Identificador único del juego.

    Returns:
        Response: Respuesta JSON de Flask con código de estado y datos relevantes o mensaje de error.
            En caso de éxito (200):
            - Para presidente humano: políticas robadas y opciones de descarte
            - Para presidente bot: elección automática y avance a canciller

            En caso de error (403/404/500):
            - error (str): Descripción del error ocurrido
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
                    "error": "Not in legislative phase",
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
            chosen, _ = game.presidential_policy_choice(draw_result["policies"])

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


@legislative_bp.route("/games/<game_id>/president/discard", methods=["POST"])
def president_discard_policy(game_id):
    """Maneja la acción del presidente de descartar una de las tres políticas legislativas.

    Args:
        game_id (str): Identificador único de la sesión de juego.

    Returns:
        Response: Respuesta JSON de Flask con:
            - 200 OK y detalles de la política descartada y siguiente fase si es exitoso.
            - 400 Bad Request si faltan datos requeridos o son inválidos.
            - 403 Forbidden si el estado del juego no permite descartar.
            - 404 Not Found si el juego no existe.
            - 500 Internal Server Error para fallos inesperados.

    Request JSON Body:
        discardIndex (int): Índice (0, 1, o 2) de la política a descartar.

    Note:
        Efectos secundarios:
        - Actualiza el estado del juego descartando la política seleccionada.
        - Avanza el juego a la fase de promulgación del canciller si es exitoso.
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


@legislative_bp.route("/games/<game_id>/chancellor/enact", methods=["POST"])
def chancellor_enact_policy(game_id):
    """Permite al canciller promulgar una de las dos políticas legislativas disponibles.

    Maneja tanto cancilleres humanos como bots, y gestiona la ejecución automática
    o manual de poderes presidenciales.

    Args:
        game_id (str): Identificador único del juego.

    Returns:
        Response: Respuesta JSON de Flask con detalles de la política promulgada
            y siguiente fase del juego.

    Request JSON Body:
        enactIndex (int, opcional): Índice (0 o 1) de la política a promulgar.
            Requerido solo para cancilleres humanos.

    Note:
        Flujo completo:
        1. Canciller humano → requiere enactIndex
        2. Canciller bot → elección automática
        3. Si se otorga poder:
           - Presidente bot → ejecución automática
           - Presidente humano → pasa a fase executive_power
        4. Sin poder → finaliza sesión y pasa a election
    """
    data = request.get_json() or {}
    enact_index = data.get("enactIndex")

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
                    "error": "Not in legislative phase",
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
        or len(game.state.chancellor_policies) != 2
    ):
        return (
            jsonify(
                {
                    "error": "Chancellor must have exactly 2 policies available",
                    "suggestion": "President must draw and discard first",
                    "currentPolicies": len(
                        getattr(game.state, "chancellor_policies", [])
                    ),
                }
            ),
            403,
        )

    try:
        chancellor = game.state.chancellor
        chancellor_is_human = getattr(chancellor, "player_type", "human") == "human"

        if chancellor_is_human:
            if enact_index is None:
                return (
                    jsonify(
                        {"error": "Missing enactIndex (0 or 1) for human chancellor"}
                    ),
                    400,
                )

            if enact_index not in [0, 1]:
                return jsonify({"error": "enactIndex must be 0 or 1"}), 400

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
                    "isHuman": True,
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

        else:
            enacted, _ = game.chancellor_policy_choice(game.state.chancellor_policies)
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
                    "name": getattr(chancellor, "name", f"Bot_{chancellor.id}"),
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
            response_data["gameOverReason"] = "Policy victory"
            return jsonify(response_data), 200

        if choice_result["power_granted"]:
            power_type = choice_result["power_granted"]
            president = game.state.president
            president_is_human = getattr(president, "player_type", "human") == "human"

            if president_is_human:
                response_data["newPhase"] = "executive_power"
                response_data["executivePower"] = {
                    "powerType": power_type,
                    "president": {
                        "id": president.id,
                        "name": getattr(president, "name", f"Player {president.id}"),
                        "isHuman": True,
                        "mustExecutePower": True,
                    },
                    "requiresHumanInput": True,
                    "instruction": f"President must execute {power_type} power",
                }
                response_data["availableActions"] = ["execute_power"]

                game.state.pending_power_type = power_type
                game.state.current_phase_name = "executive_power"

                return jsonify(response_data), 200

            else:
                power_result = execute_presidential_power(
                    game=game, power_type=power_type, target_player_id=None
                )

                if power_result.get("success", False):
                    response_data["powerExecution"] = {
                        "powerType": power_type,
                        "executedBy": {
                            "id": president.id,
                            "name": getattr(president, "name", f"Bot_{president.id}"),
                            "isBot": True,
                        },
                        "automatic": True,
                        "result": power_result,
                    }

                    if power_result.get("game_over", False):
                        response_data["gameOver"] = True
                        response_data["newPhase"] = "game_over"
                        response_data["winner"] = power_result.get("winner")
                        response_data["gameOverReason"] = (
                            "Hitler executed"
                            if power_result.get("hitler_executed")
                            else "Power execution ended game"
                        )

                        if power_result.get("target_player"):
                            response_data["executedPlayer"] = power_result[
                                "target_player"
                            ]

                        return jsonify(response_data), 200

                    session_end = end_legislative_session(game)
                    response_data["sessionEnd"] = session_end
                    response_data["newPhase"] = "election"
                    response_data["subPhase"] = "nomination"

                else:
                    response_data["powerExecutionError"] = power_result
                    response_data["newPhase"] = "executive_power"
                    response_data["executivePower"] = {
                        "powerType": power_type,
                        "president": {
                            "id": president.id,
                            "name": getattr(president, "name", f"Bot_{president.id}"),
                            "isBot": True,
                            "error": "Automatic execution failed - requires manual intervention",
                        },
                    }
                    game.state.pending_power_type = power_type
                    game.state.current_phase_name = "executive_power"

        else:
            session_end = end_legislative_session(game)
            response_data["sessionEnd"] = session_end
            response_data["newPhase"] = "election"
            response_data["subPhase"] = "nomination"

            if hasattr(game.state, "president") and game.state.president:
                response_data["nextPresident"] = {
                    "id": game.state.president.id,
                    "name": getattr(
                        game.state.president,
                        "name",
                        f"Player {game.state.president.id}",
                    ),
                }

        return jsonify(response_data), 200

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to enact policy: {str(e)}"}), 500


@legislative_bp.route("/games/<game_id>/executive/execute", methods=["POST"])
def execute_presidential_power_endpoint(game_id):
    """Permite al presidente humano ejecutar un poder presidencial.

    Args:
        game_id (str): Identificador único del juego.

    Returns:
        Response: Respuesta JSON de Flask con resultado de la ejecución del poder.
            En caso de éxito (200):
            - message (str): Mensaje de confirmación
            - powerExecution (dict): Detalles de la ejecución del poder
            - gameOver (bool, opcional): Si el juego terminó
            - sessionEnd (dict, opcional): Detalles del fin de sesión

            En caso de error (400/403/404/500):
            - error (str): Descripción del error

    Request JSON:
        powerType (str): Tipo de poder ("execution", "investigation",
            "special_election", "policy_peek").
        targetPlayerId (int, opcional): ID del jugador objetivo. Requerido
            para todos los poderes excepto policy_peek.

    Note:
        - Solo presidentes humanos pueden usar este endpoint.
        - El poder debe coincidir con el poder pendiente en el estado del juego.
        - Algunos poderes pueden terminar el juego si ejecutan a Hitler.
    """
    data = request.get_json() or {}
    power_type = data.get("powerType")
    target_player_id = data.get("targetPlayerId")

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

    if not hasattr(game.state, "president") or not game.state.president:
        return jsonify({"error": "No president assigned"}), 403

    president = game.state.president
    president_is_human = getattr(president, "player_type", "human") == "human"

    if not president_is_human:
        return jsonify({"error": "Only human presidents can use this endpoint"}), 403

    if not power_type:
        return jsonify({"error": "Missing powerType"}), 400

    expected_power = getattr(game.state, "pending_power_type", None)
    if expected_power and power_type != expected_power:
        return (
            jsonify(
                {
                    "error": "Power type mismatch",
                    "expected": expected_power,
                    "provided": power_type,
                }
            ),
            400,
        )

    if power_type not in [
        "execution",
        "investigation",
        "special_election",
        "policy_peek",
    ]:
        return jsonify({"error": f"Invalid powerType: {power_type}"}), 400

    if (
        power_type in ["execution", "investigation", "special_election"]
        and target_player_id is None
    ):
        return jsonify({"error": f"Power {power_type} requires targetPlayerId"}), 400

    try:
        power_result = execute_presidential_power(
            game=game, power_type=power_type, target_player_id=target_player_id
        )

        if power_result.get("success", False):
            response_data = {
                "message": f"Presidential power {power_type} executed successfully",
                "powerExecution": {
                    "powerType": power_type,
                    "executedBy": {
                        "id": president.id,
                        "name": getattr(president, "name", f"Player {president.id}"),
                        "isHuman": True,
                    },
                    "result": power_result,
                },
            }

            if power_result.get("game_over", False):
                response_data["gameOver"] = True
                response_data["newPhase"] = "game_over"
                response_data["winner"] = power_result.get("winner")
                response_data["gameOverReason"] = (
                    "Hitler executed"
                    if power_result.get("hitler_executed")
                    else "Power execution ended game"
                )

                if power_result.get("target_player"):
                    response_data["executedPlayer"] = power_result["target_player"]

                if hasattr(game.state, "pending_power_type"):
                    delattr(game.state, "pending_power_type")

                return jsonify(response_data), 200

            session_end = end_legislative_session(game)
            response_data["sessionEnd"] = session_end
            response_data["newPhase"] = "election"
            response_data["subPhase"] = "nomination"

            if hasattr(game.state, "pending_power_type"):
                delattr(game.state, "pending_power_type")

            return jsonify(response_data), 200

        else:
            return (
                jsonify(
                    {
                        "error": "Failed to execute presidential power",
                        "details": power_result,
                    }
                ),
                500,
            )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Failed to execute power: {str(e)}"}), 500


@legislative_bp.route("/games/<game_id>/executive/options", methods=["GET"])
def get_executive_power_options(game_id):
    """Obtiene las opciones disponibles para el poder presidencial pendiente.

    Args:
        game_id (str): Identificador único del juego.

    Returns:
        Response: Respuesta JSON de Flask con opciones disponibles para el poder.
            En caso de éxito (200):
            - powerType (str): Tipo de poder pendiente
            - requiresTarget (bool): Si el poder requiere un objetivo
            - availableTargets (list): Lista de jugadores disponibles como objetivos
            - president (dict): Información del presidente
            - instruction (str): Instrucción para el usuario

            En caso de error (403/404):
            - error (str): Descripción del error

    Note:
        - Solo disponible durante la fase executive_power.
        - Los objetivos disponibles excluyen al presidente y jugadores muertos.
        - Para policy_peek no se requieren objetivos.
    """
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

    power_type = getattr(game.state, "pending_power_type", None)
    if not power_type:
        return jsonify({"error": "No pending power found"}), 404

    president = game.state.president
    available_targets = []

    if power_type in ["execution", "investigation", "special_election"]:
        available_targets = [
            {
                "id": p.id,
                "name": getattr(p, "name", f"Player {p.id}"),
                "isAlive": not getattr(p, "is_dead", False),
            }
            for p in game.state.players
            if not getattr(p, "is_dead", False) and p != president
        ]

    elif power_type == "policy_peek":
        available_targets = []

    return (
        jsonify(
            {
                "powerType": power_type,
                "requiresTarget": power_type != "policy_peek",
                "availableTargets": available_targets,
                "president": {
                    "id": president.id,
                    "name": getattr(president, "name", f"Player {president.id}"),
                    "isHuman": getattr(president, "player_type", "human") == "human",
                },
                "instruction": (
                    f"Choose target for {power_type} power"
                    if power_type != "policy_peek"
                    else "Execute policy peek power"
                ),
            }
        ),
        200,
    )
