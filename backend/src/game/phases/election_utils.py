"""Utilidades separadas para manejar elecciones de forma granular.

Este módulo extrae funciones específicas de ElectionPhase para permitir
control granular desde el API sin duplicar lógica electoral.
"""


def check_marked_for_execution(game):
    """Verifica y ejecuta jugadores marcados para ejecución.

    Verifica si un jugador marcado para ejecución debe ser eliminado basándose en
    el número de políticas fascistas promulgadas desde que fue marcado.

    Args:
        game: Instancia del juego.

    Returns:
        dict: Resultado de la verificación de ejecución.
            - executed: Boolean indicando si se ejecutó un jugador.
            - player: Jugador ejecutado o None.
            - game_over: Boolean indicando si el juego terminó.
            - winner: String con ganador o None.
    """
    result = {"executed": False, "player": None, "game_over": False, "winner": None}

    if (
        hasattr(game.state, "marked_for_execution")
        and game.state.marked_for_execution is not None
        and hasattr(game.state, "marked_for_execution_tracker")
        and game.state.marked_for_execution_tracker is not None
    ):

        fascist_policies_enacted = (
            game.state.board.fascist_track - game.state.marked_for_execution_tracker
        )

        if fascist_policies_enacted >= 3:
            player = game.state.marked_for_execution

            player.is_dead = True
            if player in game.state.active_players:
                game.state.active_players.remove(player)

            game.state.marked_for_execution = None
            game.state.marked_for_execution_tracker = None

            result["executed"] = True
            result["player"] = player

            if getattr(player, "is_hitler", False):
                if getattr(game, "communists_in_play", False):
                    game.state.winner = "liberal_and_communist"
                else:
                    game.state.winner = "liberal"

                game.state.game_over = True
                result["game_over"] = True
                result["winner"] = game.state.winner

    return result


def nominate_chancellor_safe(game):
    """Nomina un canciller de forma segura.

    Maneja la nominación del canciller incluyendo casos especiales donde
    no hay candidatos elegibles, lo que desencadena una política de caos.

    Args:
        game: Instancia del juego.    Returns:
        dict: Resultado de la nominación.
            - nominee: Jugador nominado o None.
            - chaos_triggered: Boolean indicando si se activó política de caos.
            - game_over: Boolean indicando si el juego terminó.
            - winner: String con ganador o None.
    """
    result = {
        "nominee": None,
        "chaos_triggered": False,
        "game_over": False,
        "winner": None,
    }

    nominee = game.nominate_chancellor()

    if nominee is None:
        game.enact_chaos_policy()
        game.state.election_tracker = 0
        result["chaos_triggered"] = True

        if game.check_policy_win():
            result["game_over"] = True
            result["winner"] = getattr(game.state, "winner", "unknown")
        else:
            game.state.term_limited_players = []
            advance_to_next_president(game)
    else:
        game.state.chancellor_candidate = nominee
        result["nominee"] = nominee

    return result


def resolve_election(game, votes_dict):
    """Resuelve la elección con votos dados.

    Procesa los votos de todos los jugadores y determina si la elección
    fue exitosa o fallida, manejando las consecuencias correspondientes.

    Args:
        game: Instancia del juego.
        votes_dict (dict): Diccionario con votos {player_id: bool}.

    Returns:
        dict: Resultado de la resolución electoral.
            - passed: Boolean indicando si la elección pasó.
            - ja_votes: Número entero de votos a favor.
            - nein_votes: Número entero de votos en contra.
            - total_votes: Número total de votos.
            - government_installed: Boolean indicando si se instaló el gobierno.
            - game_over: Boolean indicando si el juego terminó.
            - winner: String con ganador o None.
            - next_phase: String con nombre de la siguiente fase.
    """
    # Transferir votos al sistema del backend
    game.state.last_votes = [
        votes_dict.get(p.id, False)
        for p in game.state.players
        if getattr(p, "is_alive", True)
    ]

    # Calcular resultado
    ja_votes = sum(1 for v in game.state.last_votes if v)
    total_votes = len(game.state.last_votes)
    vote_passed = ja_votes > total_votes // 2

    result = {
        "passed": vote_passed,
        "ja_votes": ja_votes,
        "nein_votes": total_votes - ja_votes,
        "total_votes": total_votes,
        "government_installed": False,
        "game_over": False,
        "winner": None,
        "next_phase": "election",
    }

    if vote_passed:
        # ✅ ELECCIÓN EXITOSA

        # Verificar Hitler Chancellor win condition
        if (
            game.state.fascist_track >= 3
            and hasattr(game.state.chancellor_candidate, "is_hitler")
            and game.state.chancellor_candidate.is_hitler
        ):

            game.state.winner = "fascist"
            game.state.game_over = True
            result["game_over"] = True
            result["winner"] = "fascist"
            result["next_phase"] = "game_over"
            return result

        # Instalar gobierno
        install_government(game)
        result["government_installed"] = True
        result["next_phase"] = "legislative"

    else:
        # ❌ ELECCIÓN FALLIDA

        # Avanzar election tracker
        game.state.election_tracker += 1

        # Verificar chaos (3 elecciones fallidas)
        if game.state.election_tracker >= 3:
            game.enact_chaos_policy()
            game.state.election_tracker = 0

            # Verificar victoria después de chaos
            if game.check_policy_win():
                result["game_over"] = True
                result["winner"] = getattr(game.state, "winner", "unknown")
                result["next_phase"] = "game_over"
                return result

            # Reset term limits
            game.state.term_limited_players = []

        # Limpiar candidato y avanzar presidente
        game.state.chancellor_candidate = None
        advance_to_next_president(game)

    return result


def install_government(game):
    """Instalar gobierno después de elección exitosa.

    Basado en ElectionPhase.execute() government installation
    """
    # Guardar gobierno anterior
    if (
        hasattr(game.state, "president")
        and game.state.president
        and hasattr(game.state, "chancellor")
        and game.state.chancellor
    ):
        game.state.previous_government = {
            "president": game.state.president.id,
            "chancellor": game.state.chancellor.id,
        }

    # Instalar nuevo gobierno
    game.state.president = getattr(
        game.state, "president_candidate", game.state.president
    )
    game.state.chancellor = game.state.chancellor_candidate

    # Limpiar candidatos
    game.state.chancellor_candidate = None

    # Reset election tracker
    game.state.election_tracker = 0

    # Actualizar fase
    game.state.current_phase_name = "legislative"


def advance_to_next_president(game):
    """Avanzar al siguiente presidente.

    Basado en ElectionPhase._advance_to_next_president()
    """
    game.set_next_president()

    # Asegurar que president_candidate esté establecido
    if hasattr(game.state, "president") and game.state.president:
        game.state.president_candidate = game.state.president


def run_full_election_cycle(game):
    """Ejecutar ciclo completo de elección automática.

    Equivalente a ElectionPhase.execute() completo

    Returns:
        dict: Resultado completo de la elección
    """
    # 1. Verificar ejecuciones pendientes
    execution_result = check_marked_for_execution(game)
    if execution_result["game_over"]:
        return {
            "phase": "execution",
            "game_over": True,
            "winner": execution_result["winner"],
            "executed_player": execution_result["player"],
        }

    # 2. Nominación
    nomination_result = nominate_chancellor_safe(game)
    if nomination_result["game_over"]:
        return {
            "phase": "nomination_chaos",
            "game_over": True,
            "winner": nomination_result["winner"],
            "chaos_triggered": True,
        }

    if nomination_result["chaos_triggered"]:
        return {
            "phase": "nomination_chaos",
            "game_over": False,
            "chaos_triggered": True,
            "next_phase": "election",
        }

    # 3. Votación automática (todos los bots votan)
    votes = {}
    for player in game.state.players:
        if getattr(player, "is_alive", True):
            votes[player.id] = player.vote()

    # 4. Resolución
    election_result = resolve_election(game, votes)

    return {
        "phase": "full_election",
        "nomination": {
            "nominee": nomination_result["nominee"],
            "president": game.state.president,
        },
        "election_result": election_result,
        "game_over": election_result["game_over"],
        "winner": election_result["winner"],
        "next_phase": election_result["next_phase"],
    }
