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

    if not all(0 <= i < 3 for i in policy_indices):
        return {"success": False, "error": "Policy indices must be 0, 1, or 2"}

    chosen_policies = [policies[i] for i in policy_indices]
    discarded_policy = [policies[i] for i in range(3) if i not in policy_indices][0]

    game.state.board.discard(discarded_policy)
    game.state.chancellor_policies = chosen_policies

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

    if getattr(game.state.chancellor, "player_type", "human") == "ai":
        chancellor_proposes = game.chancellor_propose_veto()
    else:
        chancellor_proposes = None

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
        if hasattr(game.state, "chancellor_policies"):
            game.state.board.discard(game.state.chancellor_policies)
            game.state.chancellor_policies = None

        game.state.election_tracker += 1

        return {
            "veto_accepted": True,
            "policies_discarded": True,
            "election_tracker_advanced": True,
            "next_phase": "election",
        }
    else:
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

    enacted_policy = policies[policy_index]
    discarded_policy = policies[1 - policy_index]

    game.state.board.discard(discarded_policy)

    power_granted = game.state.board.enact_policy(
        enacted_policy,
        False,
        getattr(game, "emergency_powers_in_play", False),
        getattr(game, "anti_policies_in_play", False),
    )

    game.state.chancellor_policies = None

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
    """Ejecutar poder presidencial con lógica separada para humanos y bots.

    Args:
        game: Instancia del juego
        power_type: str - tipo de poder a ejecutar
        target_player_id: int - ID del jugador objetivo (SOLO para humanos)
        peek_choice: any - decisión para peek de políticas

    Returns:
        dict: Resultado de la ejecución del poder
    """
    try:
        president = game.state.president
        if not president:
            return {"success": False, "error": "No president assigned"}

        president_is_human = getattr(president, "player_type", "human") == "human"

        if not president_is_human:
            return _execute_power_for_bot(game, power_type)

        else:
            return _execute_power_for_human(game, power_type, target_player_id)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "error": f"Failed to execute power {power_type}: {str(e)}",
        }


def _execute_power_for_bot(game, power_type):
    """Ejecutar poder para presidente BOT usando lógica automática del juego."""
    try:
        result = game.execute_power(power_type)

        if power_type == "execution":
            hitler_executed = getattr(result, "is_hitler", False) if result else False

            if hitler_executed:
                game.state.game_over = True
                if getattr(game, "communists_in_play", False):
                    game.state.winner = "liberal_and_communist"
                else:
                    game.state.winner = "liberal"

                return {
                    "power_executed": power_type,
                    "target_player": {
                        "id": result.id,
                        "name": getattr(result, "name", f"Player {result.id}"),
                        "was_hitler": True,
                    },
                    "result": {
                        "player_id": result.id,
                        "player_name": getattr(result, "name", f"Player {result.id}"),
                        "was_hitler": True,
                        "is_alive": False,
                        "execution_successful": True,
                    },
                    "game_over": True,
                    "winner": game.state.winner,
                    "hitler_executed": True,
                    "success": True,
                }
            else:
                return {
                    "power_executed": power_type,
                    "target_player": {
                        "id": result.id,
                        "name": getattr(result, "name", f"Player {result.id}"),
                        "was_hitler": False,
                    },
                    "result": {
                        "player_id": result.id,
                        "player_name": getattr(result, "name", f"Player {result.id}"),
                        "was_hitler": False,
                        "is_alive": getattr(result, "is_alive", False),
                        "execution_successful": True,
                    },
                    "game_over": False,
                    "winner": None,
                    "hitler_executed": False,
                    "success": True,
                }

        elif power_type == "investigation":
            return {
                "power_executed": power_type,
                "target_player": {
                    "id": result.id if result else None,
                    "name": getattr(result, "name", "Unknown") if result else "Unknown",
                    "party": (
                        getattr(result, "party_membership", "unknown")
                        if result
                        else "unknown"
                    ),
                },
                "result": {
                    "player_id": result.id if result else None,
                    "player_name": (
                        getattr(result, "name", "Unknown") if result else "Unknown"
                    ),
                    "party_membership": (
                        getattr(result, "party_membership", "unknown")
                        if result
                        else "unknown"
                    ),
                },
                "game_over": False,
                "winner": None,
                "hitler_executed": False,
                "success": True,
            }

        elif power_type == "special_election":
            return {
                "power_executed": power_type,
                "target_player": {
                    "id": result.id if result else None,
                    "name": getattr(result, "name", "Unknown") if result else "Unknown",
                },
                "result": {"new_president": result.id if result else None},
                "game_over": False,
                "winner": None,
                "hitler_executed": False,
                "success": True,
            }

        elif power_type == "policy_peek":
            if (
                hasattr(game.state.board, "policies")
                and len(game.state.board.policies) < 3
            ):
                if hasattr(game.state.board, "reshuffle"):
                    game.state.board.reshuffle()
            top_policies = []
            policy_names = []
            if (
                hasattr(game.state.board, "policies")
                and len(game.state.board.policies) >= 3
            ):
                top_policies = game.state.board.policies[:3]
                policy_names = [
                    getattr(policy, "type", str(policy)) for policy in top_policies
                ]
            return {
                "power_executed": power_type,
                "target_player": None,
                "result": {
                    "top_policies": policy_names,
                    "message": "President peeked at top policies",
                },
                "game_over": False,
                "winner": None,
                "hitler_executed": False,
                "success": True,
            }

        else:
            return {
                "power_executed": power_type,
                "target_player": None,
                "result": {"value": str(result) if result else None},
                "game_over": False,
                "winner": None,
                "hitler_executed": False,
                "success": True,
            }

    except Exception as e:
        return {"success": False, "error": f"Bot power execution failed: {str(e)}"}


def _execute_power_for_human(game, power_type, target_player_id):
    """Ejecutar poder para presidente HUMANO usando target_player_id."""

    if power_type == "execution":
        if target_player_id is None:
            return {
                "success": False,
                "error": "Human president must provide target_player_id for execution",
            }

        target_player = None
        for player in game.state.players:
            if player.id == target_player_id:
                target_player = player
                break

        if not target_player:
            return {"success": False, "error": "Target player not found"}

        if not getattr(target_player, "is_alive", True):
            return {"success": False, "error": "Target player is already dead"}

        target_player.is_alive = False

        if (
            hasattr(game.state, "active_players")
            and target_player in game.state.active_players
        ):
            game.state.active_players.remove(target_player)

        hitler_executed = getattr(target_player, "is_hitler", False)

        if hitler_executed:
            game.state.game_over = True
            if getattr(game, "communists_in_play", False):
                game.state.winner = "liberal_and_communist"
            else:
                game.state.winner = "liberal"

            if hasattr(game, "logger"):
                game.logger.log_player_death(target_player)
                if game.communists_in_play:
                    game.logger.log("Hitler was executed! Liberals and Communists win!")
                else:
                    game.logger.log("Hitler was executed! Liberals win!")

            return {
                "power_executed": power_type,
                "target_player": {
                    "id": target_player.id,
                    "name": getattr(
                        target_player, "name", f"Player {target_player.id}"
                    ),
                    "was_hitler": True,
                },
                "result": {
                    "player_id": target_player.id,
                    "player_name": getattr(
                        target_player, "name", f"Player {target_player.id}"
                    ),
                    "was_hitler": True,
                    "is_alive": False,
                    "execution_successful": True,
                },
                "game_over": True,
                "winner": game.state.winner,
                "hitler_executed": True,
                "success": True,
            }
        else:
            if hasattr(game, "logger"):
                game.logger.log_player_death(target_player)

            return {
                "power_executed": power_type,
                "target_player": {
                    "id": target_player.id,
                    "name": getattr(
                        target_player, "name", f"Player {target_player.id}"
                    ),
                    "was_hitler": False,
                },
                "result": {
                    "player_id": target_player.id,
                    "player_name": getattr(
                        target_player, "name", f"Player {target_player.id}"
                    ),
                    "was_hitler": False,
                    "is_alive": False,
                    "execution_successful": True,
                },
                "game_over": False,
                "winner": None,
                "hitler_executed": False,
                "success": True,
            }

    elif power_type == "investigation":
        if target_player_id is None:
            return {
                "success": False,
                "error": "Human president must provide target_player_id for investigation",
            }

        target_player = None
        for player in game.state.players:
            if player.id == target_player_id:
                target_player = player
                break

        if not target_player:
            return {"success": False, "error": "Target player not found"}

        party = getattr(target_player, "party_membership", "liberal")

        if hasattr(game, "logger"):
            game.logger.log_power_used(
                power_type, game.state.president, target_player, party
            )

        return {
            "power_executed": power_type,
            "target_player": {
                "id": target_player.id,
                "name": getattr(target_player, "name", f"Player {target_player.id}"),
                "party": party,
            },
            "result": {"party_membership": party},
            "game_over": False,
            "winner": None,
            "hitler_executed": False,
            "success": True,
        }

    elif power_type == "special_election":
        if target_player_id is None:
            return {
                "success": False,
                "error": "Human president must provide target_player_id for special election",
            }

        target_player = None
        for player in game.state.players:
            if player.id == target_player_id:
                target_player = player
                break

        if not target_player:
            return {"success": False, "error": "Target player not found"}

        game.state.president = target_player
        game.state.president_candidate = target_player

        if hasattr(game, "logger"):
            game.logger.log_power_used(
                power_type, game.state.president, target_player, target_player
            )

        return {
            "power_executed": power_type,
            "target_player": {
                "id": target_player.id,
                "name": getattr(target_player, "name", f"Player {target_player.id}"),
            },
            "result": {"new_president": target_player.id},
            "game_over": False,
            "winner": None,
            "hitler_executed": False,
            "success": True,
        }

    elif power_type == "policy_peek":
        top_policies = []
        policy_names = []
        if hasattr(game.state.board, "policies") and len(game.state.board.policies) < 3:
            if hasattr(game.state.board, "reshuffle"):
                game.state.board.reshuffle()

        if (
            hasattr(game.state.board, "policies")
            and len(game.state.board.policies) >= 3
        ):
            top_policies = game.state.board.policies[:3]
            policy_names = [policy.type for policy in top_policies]

        if hasattr(game, "logger"):
            game.logger.log_power_used(
                power_type, game.state.president, None, policy_names
            )

        return {
            "power_executed": power_type,
            "target_player": None,
            "result": {
                "top_policies": policy_names,
                "deck_remaining": (
                    len(game.state.board.policies)
                    if hasattr(game.state.board, "policies")
                    else 0
                ),
            },
            "game_over": False,
            "winner": None,
            "hitler_executed": False,
            "success": True,
        }

    else:
        return {"success": False, "error": f"Unknown power type: {power_type}"}


def end_legislative_session(game):
    """Finalizar sesión legislativa y preparar siguiente elección."""

    set_term_limits(game)

    current_president = game.state.president
    current_president_id = current_president.id if current_president else None

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

    next_president = None
    if current_president and hasattr(game.state, "active_players"):
        active_players = game.state.active_players

        try:
            current_index = active_players.index(current_president)
            next_index = (current_index + 1) % len(active_players)
            next_president = active_players[next_index]

        except ValueError:
            print(
                f"ERROR: Current president {current_president_id} not found in active_players"
            )
            if active_players:
                next_president = active_players[0]
                print(f"FALLBACK: Using first active player: {next_president.id}")

    if next_president:
        game.state.president = next_president
        game.state.president_candidate = next_president

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
        if last_chancellor_served:
            game.state.term_limited_players.append(last_chancellor_served)
    else:
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
    presidential_draw = draw_presidential_policies(game)
    game.state.presidential_policies = presidential_draw["policies"]

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

    veto_check = check_veto_proposal(game)
    if veto_check["veto_available"] and veto_check["chancellor_proposes"]:
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

    if game.check_policy_win():
        return {
            "phase": "policy_win",
            "game_over": True,
            "winner": getattr(game.state, "winner", "unknown"),
            "next_phase": "game_over",
        }

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
