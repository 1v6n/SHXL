"""Utilidades separadas para manejar la fase legislativa de forma granular.

Este módulo extrae funciones específicas de LegislativePhase para permitir
control granular desde el API sin duplicar lógica.

Funciones extraídas de: src/game/phases/legislative.py
"""


def draw_presidential_policies(game):
    """Dibujar 3 políticas para decisión presidencial.

    Extraído de: LegislativePhase.execute() - policy drawing

    Args:
        game: Instancia del juego SHXLGame

    Returns:
        dict: {
            "policies": [Policy, Policy, Policy],
            "policy_names": [str, str, str],
            "deck_remaining": int
        }
    """
    policies = game.state.board.draw_policy(3)

    return {
        "policies": policies,
        "policy_names": [policy.type for policy in policies],
        "deck_remaining": len(game.state.board.policies),
    }


def handle_presidential_choice(game, policy_indices):
    """Manejar decisión presidencial de políticas.

    Extraído de: LegislativePhase.execute() - presidential choice

    Args:
        game: Instancia del juego
        policy_indices: [int] - índices de políticas a mantener (2 de 3)

    Returns:
        dict: {
            "chosen_policies": [Policy, Policy],
            "discarded_policy": Policy,
            "chosen_names": [str, str],
            "discarded_name": str,
            "success": bool
        }
    """
    if not hasattr(game.state, "presidential_policies"):
        return {"success": False, "error": "No presidential policies available"}

    policies = game.state.presidential_policies

    if len(policy_indices) != 2 or len(policies) != 3:
        return {"success": False, "error": "Must choose exactly 2 policies from 3"}

    # Validar índices
    if not all(0 <= i < 3 for i in policy_indices):
        return {"success": False, "error": "Policy indices must be 0, 1, or 2"}

    # Separar elegidas y descartada
    chosen_policies = [policies[i] for i in policy_indices]
    discarded_policy = [policies[i] for i in range(3) if i not in policy_indices][0]

    # Aplicar decisión
    game.state.board.discard(discarded_policy)
    game.state.chancellor_policies = chosen_policies

    # Limpiar políticas presidenciales
    game.state.presidential_policies = None

    return {
        "chosen_policies": chosen_policies,
        "discarded_policy": discarded_policy,
        "chosen_names": [policy.type for policy in chosen_policies],
        "discarded_name": discarded_policy.type,
        "success": True,
    }


def check_veto_proposal(game):
    """Verificar si el canciller puede/quiere proponer veto.

    Extraído de: LegislativePhase.execute() - veto proposal

    Args:
        game: Instancia del juego

    Returns:
        dict: {
            "veto_available": bool,
            "chancellor_proposes": bool,
            "can_veto": bool
        }
    """
    veto_available = game.state.board.veto_available

    if not veto_available:
        return {
            "veto_available": False,
            "chancellor_proposes": False,
            "can_veto": False,
        }

    # Para bots: usar su decisión automática
    if getattr(game.state.chancellor, "player_type", "human") == "ai":
        chancellor_proposes = game.chancellor_propose_veto()
    else:
        # Para humanos: requerir decisión manual
        chancellor_proposes = None  # Se decidirá en el API

    return {
        "veto_available": True,
        "chancellor_proposes": chancellor_proposes,
        "can_veto": True,
    }


def handle_veto_decision(game, president_accepts_veto):
    """Manejar decisión presidencial sobre veto.

    Extraído de: LegislativePhase.execute() - veto resolution

    Args:
        game: Instancia del juego
        president_accepts_veto: bool - si el presidente acepta el veto

    Returns:
        dict: {
            "veto_accepted": bool,
            "policies_discarded": bool,
            "election_tracker_advanced": bool,
            "next_phase": str
        }
    """
    if president_accepts_veto:
        # Presidente acepta veto - descartar políticas
        if hasattr(game.state, "chancellor_policies"):
            game.state.board.discard(game.state.chancellor_policies)
            game.state.chancellor_policies = None

        # Avanzar election tracker
        game.state.election_tracker += 1

        return {
            "veto_accepted": True,
            "policies_discarded": True,
            "election_tracker_advanced": True,
            "next_phase": "election",
        }
    else:
        # Presidente rechaza veto - continuar con decisión del canciller
        return {
            "veto_accepted": False,
            "policies_discarded": False,
            "election_tracker_advanced": False,
            "next_phase": "chancellor_choice",
        }


def handle_chancellor_choice(game, policy_index):
    """Manejar decisión del canciller sobre qué política promulgar.

    Extraído de: LegislativePhase.execute() - chancellor choice

    Args:
        game: Instancia del juego
        policy_index: int - índice de la política a promulgar (0 o 1)

    Returns:
        dict: {
            "enacted_policy": Policy,
            "discarded_policy": Policy,
            "enacted_name": str,
            "discarded_name": str,
            "power_granted": str or None,
            "game_over": bool,
            "winner": str or None,
            "success": bool
        }
    """
    if (
        not hasattr(game.state, "chancellor_policies")
        or not game.state.chancellor_policies
    ):
        return {"success": False, "error": "No chancellor policies available"}

    policies = game.state.chancellor_policies

    if len(policies) != 2:
        return {"success": False, "error": "Chancellor must have exactly 2 policies"}

    if policy_index not in [0, 1]:
        return {"success": False, "error": "Policy index must be 0 or 1"}

    # Separar promulgada y descartada
    enacted_policy = policies[policy_index]
    discarded_policy = policies[1 - policy_index]

    # Descartar política no elegida
    game.state.board.discard(discarded_policy)

    # Promulgar política elegida
    power_granted = game.state.board.enact_policy(
        enacted_policy,
        False,  # chaos=False
        getattr(game, "emergency_powers_in_play", False),
        getattr(game, "anti_policies_in_play", False),
    )

    # Limpiar políticas del canciller
    game.state.chancellor_policies = None

    # Verificar victoria por políticas
    game_over = False
    winner = None
    if game.check_policy_win():
        game_over = True
        winner = getattr(game.state, "winner", "unknown")

    return {
        "enacted_policy": enacted_policy,
        "discarded_policy": discarded_policy,
        "enacted_name": enacted_policy.type,
        "discarded_name": discarded_policy.type,
        "power_granted": power_granted,
        "game_over": game_over,
        "winner": winner,
        "success": True,
    }


def execute_presidential_power(
    game, power_type, target_player_id=None, peek_choice=None
):
    """Ejecutar poder presidencial.

    Extraído de: LegislativePhase.execute() - power execution

    Args:
        game: Instancia del juego
        power_type: str - tipo de poder a ejecutar
        target_player_id: int - ID del jugador objetivo (para poderes que lo requieren)
        peek_choice: any - decisión para peek de políticas

    Returns:
        dict: {
            "power_executed": str,
            "target_player": dict or None,
            "result": any,
            "game_over": bool,
            "winner": str or None,
            "hitler_executed": bool
        }
    """
    if power_type == "execution":
        if target_player_id is None:
            return {
                "success": False,
                "error": "Execution power requires target_player_id",
            }

        # Encontrar jugador objetivo
        target_player = None
        for player in game.state.players:
            if player.id == target_player_id:
                target_player = player
                break

        if not target_player:
            return {"success": False, "error": "Target player not found"}

        # Ejecutar poder
        result = game.execute_power(power_type, target_player)

        # Verificar si era Hitler
        hitler_executed = getattr(result, "is_hitler", False) if result else False

        game_over = False
        winner = None

        if hitler_executed:
            game.state.game_over = True
            if getattr(game, "communists_in_play", False):
                game.state.winner = "liberal_and_communist"
            else:
                game.state.winner = "liberal"

            game_over = True
            winner = game.state.winner

        return {
            "power_executed": power_type,
            "target_player": {
                "id": target_player.id,
                "name": getattr(target_player, "name", f"Player {target_player.id}"),
                "was_hitler": hitler_executed,
            },
            "result": result,
            "game_over": game_over,
            "winner": winner,
            "hitler_executed": hitler_executed,
            "success": True,
        }

    elif power_type in ["investigation", "policy_peek", "call_special_election"]:
        # Otros poderes (implementar según necesidad)
        result = game.execute_power(power_type, target_player_id)

        return {
            "power_executed": power_type,
            "target_player": {"id": target_player_id} if target_player_id else None,
            "result": result,
            "game_over": False,
            "winner": None,
            "hitler_executed": False,
            "success": True,
        }

    else:
        return {"success": False, "error": f"Unknown power type: {power_type}"}


def end_legislative_session(game):
    """Finalizar sesión legislativa y preparar siguiente elección."""

    # Establecer límites de mandato
    set_term_limits(game)

    # Capturar estado antes de rotación
    current_president = game.state.president
    current_president_id = current_president.id if current_president else None

    # Guardar gobierno anterior
    previous_government = None
    if (
        hasattr(game.state, "president")
        and game.state.president
        and hasattr(game.state, "chancellor")
        and game.state.chancellor
    ):
        previous_government = {
            "president": {
                "id": game.state.president.id,
                "name": getattr(
                    game.state.president, "name", f"Player {game.state.president.id}"
                ),
            },
            "chancellor": {
                "id": game.state.chancellor.id,
                "name": getattr(
                    game.state.chancellor, "name", f"Player {game.state.chancellor.id}"
                ),
            },
        }

        game.state.previous_government = {
            "president": game.state.president.id,
            "chancellor": game.state.chancellor.id,
        }

    # 🔧 FIX: ROTACIÓN MANUAL ROBUSTA
    next_president = None
    if current_president and hasattr(game.state, "active_players"):
        active_players = game.state.active_players

        # Encontrar índice del presidente actual
        try:
            current_index = active_players.index(current_president)
            next_index = (current_index + 1) % len(active_players)
            next_president = active_players[next_index]

        except ValueError:
            print(
                f"ERROR: Current president {current_president_id} not found in active_players"
            )
            # Fallback: usar primer jugador activo
            if active_players:
                next_president = active_players[0]
                print(f"FALLBACK: Using first active player: {next_president.id}")

    # 🔧 ESTABLECER NUEVO PRESIDENTE MANUALMENTE
    if next_president:
        game.state.president = next_president
        game.state.president_candidate = next_president

        # Incrementar round number
        if hasattr(game.state, "round_number"):
            game.state.round_number += 1

        print(f"SUCCESS: New president set to: {next_president.id}")
    else:
        print("ERROR: Could not determine next president!")

    final_president_id = game.state.president.id if game.state.president else None
    final_candidate_id = (
        game.state.president_candidate.id if game.state.president_candidate else None
    )

    if final_president_id == current_president_id:
        print(f"ERROR: President did NOT change! Still {current_president_id}")
    else:
        print(
            f"SUCCESS: President rotated from {current_president_id} to {final_president_id}"
        )

    # Limpiar posiciones de gobierno
    game.state.chancellor = None
    game.state.chancellor_candidate = None
    game.state.current_phase_name = "election"

    return {
        "term_limits_set": True,
        "previous_government": previous_government,
        "turn_advanced": True,
        "next_phase": "election",
        "debug": {
            "original_president": current_president_id,
            "final_president": final_president_id,
            "rotation_successful": final_president_id != current_president_id,
        },
    }


def set_term_limits(game):
    """Establecer límites de mandato basados en gobierno actual.

    Extraído de: LegislativePhase._set_term_limits()

    Args:
        game: Instancia del juego
    """
    game.state.term_limited_players = []

    last_president_served = game.state.president
    last_chancellor_served = game.state.chancellor

    if len(game.state.active_players) > 5:
        # En juegos con más de 5 jugadores, solo el canciller tiene límite de mandato
        if last_chancellor_served:
            game.state.term_limited_players.append(last_chancellor_served)
    else:
        # En juegos con 5 o menos jugadores, ambos tienen límite de mandato
        if last_chancellor_served:
            game.state.term_limited_players.append(last_chancellor_served)
        if last_president_served and last_president_served != last_chancellor_served:
            game.state.term_limited_players.append(last_president_served)


def run_full_legislative_cycle(game):
    """Ejecutar ciclo legislativo completo automáticamente.

    Equivalente a LegislativePhase.execute() completo

    Returns:
        dict: Resultado completo de la fase legislativa (SOLO DICCIONARIOS SERIALIZABLES)
    """
    # 1. Dibujar políticas presidenciales
    presidential_draw = draw_presidential_policies(game)
    game.state.presidential_policies = presidential_draw["policies"]

    # 2. Decisión presidencial automática (si es bot)
    if getattr(game.state.president, "player_type", "human") == "ai":
        chosen, discarded = game.presidential_policy_choice(
            presidential_draw["policies"]
        )
        game.state.board.discard(discarded)
        game.state.chancellor_policies = chosen

        presidential_choice = {
            "chosen_names": [policy.type for policy in chosen],
            "discarded_name": discarded.type,
            "automatic": True,
        }
    else:
        return {
            "phase": "presidential_choice",
            "presidential_draw": {
                "policy_names": presidential_draw["policy_names"],
                "deck_remaining": presidential_draw["deck_remaining"],
            },
            "requires_human_input": True,
            "next_step": "presidential_choice",
        }

    # 3. Verificar veto
    veto_check = check_veto_proposal(game)
    if veto_check["veto_available"] and veto_check["chancellor_proposes"]:
        # Decisión presidencial sobre veto (automática si es bot)
        if getattr(game.state.president, "player_type", "human") == "ai":
            president_accepts = game.president_veto_accepted()
            veto_result = handle_veto_decision(game, president_accepts)

            if veto_result["veto_accepted"]:
                return {
                    "phase": "veto_accepted",
                    "veto_result": veto_result,
                    "next_phase": "election",
                }
        else:
            return {
                "phase": "veto_decision",
                "veto_proposed": True,
                "requires_human_input": True,
                "next_step": "veto_decision",
            }

    # 4. Decisión del canciller automática (si es bot)
    if getattr(game.state.chancellor, "player_type", "human") == "ai":
        enacted, discarded = game.chancellor_policy_choice(
            game.state.chancellor_policies
        )
        game.state.board.discard(discarded)

        power_granted = game.state.board.enact_policy(
            enacted,
            False,
            getattr(game, "emergency_powers_in_play", False),
            getattr(game, "anti_policies_in_play", False),
        )

        chancellor_choice = {
            "enacted_name": enacted.type,
            "discarded_name": discarded.type,
            "power_granted": power_granted,
            "automatic": True,
        }
    else:
        return {
            "phase": "chancellor_choice",
            "chancellor_policies": [
                policy.type for policy in game.state.chancellor_policies
            ],
            "requires_human_input": True,
            "next_step": "chancellor_choice",
        }

    # 5. Verificar victoria
    if game.check_policy_win():
        return {
            "phase": "policy_win",
            "game_over": True,
            "winner": getattr(game.state, "winner", "unknown"),
            "next_phase": "game_over",
        }

    # 6. Ejecutar poder si se otorgó
    power_result = None
    if power_granted:
        if getattr(game.state.president, "player_type", "human") == "ai":
            result = game.execute_power(power_granted)

            if (
                power_granted == "execution"
                and result
                and getattr(result, "is_hitler", False)
            ):
                return {
                    "phase": "hitler_executed",
                    "game_over": True,
                    "winner": (
                        "liberal_and_communist"
                        if getattr(game, "communists_in_play", False)
                        else "liberal"
                    ),
                    "executed_player": {
                        "id": result.id,
                        "name": getattr(result, "name", f"Player {result.id}"),
                    },
                    "next_phase": "game_over",
                }

            power_result = {"power_executed": power_granted, "automatic": True}
        else:
            return {
                "phase": "executive_power",
                "power_granted": power_granted,
                "requires_human_input": True,
                "next_step": "executive_power",
            }

    # 7. Finalizar sesión legislativa
    session_end = end_legislative_session(game)

    return {
        "phase": "legislative_complete",
        "presidential_choice": presidential_choice,
        "veto_check": veto_check,
        "chancellor_choice": chancellor_choice,
        "power_result": power_result,
        "session_end": session_end,
        "next_phase": "election",
    }
