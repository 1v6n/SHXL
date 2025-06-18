"""Funciones auxiliares para el estado del juego extraídas de app.py original.

Este módulo contiene utilidades para extraer y formatear información del estado
del juego, incluyendo configuración, jugadores, gobierno, tablero y fases.
"""

import datetime


def _get_power_description(power_name):
    """Obtiene una descripción legible de un poder dado su nombre.

    Args:
        power_name (str): Nombre clave que representa el poder.

    Returns:
        str: Descripción del poder especificado. Si no se encuentra el nombre,
            retorna un mensaje por defecto indicando ejecución del poder dado.
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
    """Obtiene el nombre de la fase actual del juego.

    Esta función intenta determinar el nombre de la fase actual verificando
    varias fuentes posibles en orden:
    1. Si game.state tiene un atributo current_phase_name no vacío, se retorna.
    2. Si game tiene un atributo current_phase no vacío, se usa su nombre de clase.
    3. Si ninguno está disponible, se infiere usando _infer_phase_from_game_state.

    Args:
        game: Objeto del juego que contiene estado e información de fase.

    Returns:
        str: Nombre de la fase actual.
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
    """Infiere la fase actual del juego basándose en los atributos del estado.

    Args:
        game: Objeto que representa el juego actual, se espera que tenga un
            atributo 'state' con varias propiedades que indican el progreso.

    Returns:
        str: String que representa la fase inferida del juego. Valores posibles:
            - "game_over": El juego ha terminado.
            - "voting": El juego está en fase de votación para candidato a canciller.
            - "legislative": Presidente y canciller están establecidos, fase legislativa.
            - "election": Solo el presidente está establecido, fase de elección.
            - "setup": El juego está en configuración o ninguna otra fase coincide.
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
    """Obtiene una lista de votantes elegibles del estado actual del juego.

    Cada votante elegible se representa como un diccionario que contiene:
    - "id": Identificador único del jugador.
    - "name": Nombre del jugador (por defecto 'Player {id}' si no está establecido).
    - "hasVoted": Boolean indicando si el jugador ya ha votado.
    - "vote": Siempre establecido a None para evitar revelar votos antes del final.

    Un jugador se considera elegible si su atributo 'is_alive' es True
    (o por defecto True si no está presente).

    Args:
        game: Objeto del juego que contiene el estado actual y jugadores.

    Returns:
        List[dict]: Lista de diccionarios, cada uno representando un votante elegible.
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
    """Obtiene la configuración del objeto juego.

    Args:
        game: Objeto que representa el juego, se espera que tenga atributos
            de configuración.

    Returns:
        dict: Diccionario que contiene las siguientes opciones de configuración:
            - maxPlayers (int): Número máximo de jugadores (por defecto: 10).
            - withCommunists (bool): Si se incluyen comunistas (por defecto: False).
            - withAntiPolicies (bool): Si están habilitadas anti-políticas (por defecto: False).
            - withEmergencyPowers (bool): Si están habilitados poderes de emergencia (por defecto: False).
            - aiStrategy (str): Estrategia de IA a usar (por defecto: 'smart').
    """
    return {
        "maxPlayers": getattr(game, "player_count", 10),
        "withCommunists": getattr(game, "include_communists", False),
        "withAntiPolicies": getattr(game, "with_anti_policies", False),
        "withEmergencyPowers": getattr(game, "with_emergency_powers", False),
        "aiStrategy": getattr(game, "ai_strategy", "smart"),
    }


def _can_see_role(game, player, requesting_player_id):
    """Determina si el rol de un jugador puede ser visto por el jugador solicitante.

    Args:
        game: Instancia actual del juego que contiene el estado y reglas.
        player: Jugador cuya visibilidad de rol se está verificando.
        requesting_player_id: ID del jugador que solicita ver el rol, o None.

    Returns:
        bool: True si el jugador solicitante puede ver el rol, False en caso contrario.

    Note:
        Reglas:
        - Un jugador siempre puede ver su propio rol.
        - Todos los roles se vuelven visibles cuando el juego termina.
    """
    if requesting_player_id is not None and player.id == requesting_player_id:
        return True

    if hasattr(game.state, "game_over") and game.state.game_over:
        return True

    return False


def _get_player_special_status(game, player):
    """Obtiene una lista de estados especiales para un jugador dado.

    Verifica los atributos de EnhancedGameState para determinar si el jugador está:
    - "term_limited": El jugador está en la lista de jugadores con límite de términos.
    - "investigated": El jugador está en la lista de jugadores investigados.
    - "marked_for_execution": El jugador está marcado para ejecución.

    Args:
        game: Objeto del juego que contiene el estado actual.
        player: Objeto jugador o identificador a verificar.

    Returns:
        list: Lista de strings de estado que representan los estados especiales del jugador.
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
    """Obtiene el timestamp actual como string formateado ISO 8601.

    Returns:
        str: Fecha y hora actual en formato ISO 8601.
    """
    return datetime.datetime.now().isoformat()


def _get_game_state_status(game):
    """Determina el estado actual del juego.

    Args:
        game: Instancia del juego a evaluar.

    Returns:
        str: Estado del juego, puede ser "game_over", "in_progress" o "waiting_for_players".
    """
    if hasattr(game.state, "game_over") and game.state.game_over:
        return "game_over"
    elif hasattr(game.state, "president") and game.state.president:
        return "in_progress"
    else:
        return "waiting_for_players"


def _get_current_phase_info(game):
    """Obtiene información sobre la fase actual del juego.

    Args:
        game: Objeto que representa el estado actual del juego. Se espera que tenga
            un atributo 'state' con al menos una propiedad 'current_phase_name',
            y posiblemente otros atributos específicos de fase.

    Returns:
        dict: Diccionario que contiene detalles sobre la fase actual, incluyendo:
            - 'name': Nombre interno de la fase.
            - 'displayName': Nombre de visualización amigable para la fase.
            - 'description': Descripción de la fase.
            - 'originalClass': Nombre de clase original para la fase.
            - 'canAdvance': Boolean indicando si la fase puede avanzar.
            - 'subPhase' (opcional): Sub-fase actual, si aplica ('voting', 'nomination', etc.).

    Note:
        La función determina la sub-fase para fases 'election' y 'legislative'
        basándose en la presencia y estado de atributos específicos en el estado del juego.
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
    """Obtiene el nombre de visualización para una fase dada.

    Args:
        phase_name (str): Nombre interno de la fase.

    Returns:
        str: Nombre de visualización en español para la fase si existe en el mapeo,
            de lo contrario retorna la versión title-case del nombre de fase de entrada.
    """
    names = {
        "setup": "Configuración",
        "election": "Elección",
        "legislative": "Legislativa",
        "game_over": "Juego Terminado",
    }
    return names.get(phase_name, phase_name.title())


def _get_phase_description(game, phase_name):
    """Obtiene una descripción legible para la fase actual del juego.

    Args:
        game: Objeto del juego que contiene el estado actual.
        phase_name (str): Nombre de la fase actual.

    Returns:
        str: Descripción de la fase actual, o string formateado para fases desconocidas.

    Note:
        Fases:
        - "setup": Retorna "Configurando el juego".
        - "election": Retorna "Nominar y votar canciller".
        - "legislative": Retorna "Seleccionar y promulgar políticas".
        - "game_over": Retorna "Juego terminado - Ganador: <winner>".
        - Cualquier otra fase: Retorna "Fase: <phase_name>".
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


def _safe_winner_string(winner):
    """Convierte ganador a formato de string seguro.

    Args:
        winner: Objeto ganador en varios formatos posibles.

    Returns:
        str: Representación string del ganador.
    """
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


def _get_players_info(game, requesting_player_id=None):
    """Obtiene información de jugadores con visibilidad de rol apropiada.

    Args:
        game: Instancia del juego.
        requesting_player_id: ID del jugador que solicita la información (no utilizado).

    Returns:
        list: Lista de diccionarios con información de cada jugador incluyendo
            ID, nombre, posición, estado vital, tipo y rol.
    """
    players_info = []

    for player in game.state.players:
        player_info = {
            "id": getattr(player, "id", -1),
            "name": getattr(player, "name", f"Player {getattr(player, 'id', '?')}"),
            "position": getattr(player, "id", -1),
            "isAlive": not getattr(player, "is_dead", False),
            "isHuman": getattr(player, "player_type", "human") == "human",
            "isBot": getattr(player, "player_type", "human") == "ai",
            "specialStatus": [],
        }

        is_hitler = getattr(player, "is_hitler", False)
        is_fascist = getattr(player, "is_fascist", False) and not is_hitler
        is_liberal = getattr(player, "is_liberal", False)
        is_communist = getattr(player, "is_communist", False)

        if is_hitler or is_fascist:
            party = "fascist"
        elif is_communist:
            party = "communist"
        else:
            party = "liberal"

        role_info = {
            "isVisible": True,
            "party": party,
            "isLiberal": is_liberal,
            "isFascist": is_fascist,
            "isHitler": is_hitler,
            "isCommunist": is_communist,
        }

        player_info["role"] = role_info

        if (
            hasattr(game.state, "previous_government")
            and game.state.previous_government
        ):
            if player.id == game.state.previous_government.get(
                "president"
            ) or player.id == game.state.previous_government.get("chancellor"):
                player_info["specialStatus"].append("term_limited")

        players_info.append(player_info)

    return players_info


def _get_government_info(game):
    """Obtiene información estructurada sobre el estado del gobierno actual y anterior.

    Args:
        game: Instancia del juego que contiene el estado actual e información de jugadores.

    Returns:
        dict: Diccionario con las siguientes claves:
            - "president": Información sobre el presidente actual (id y nombre), o None.
            - "chancellor": Información sobre el canciller actual (id y nombre), o None.
            - "presidentCandidate": Información sobre candidato a presidente actual, o None.
            - "chancellorCandidate": Información sobre candidato a canciller actual, o None.
            - "previousGovernment": Diccionario con presidente y canciller anterior, o None.
            - "termLimited": Lista de jugadores actualmente con límite de términos.

    Note:
        Los nombres de jugadores se obtienen del objeto jugador si están disponibles;
        de lo contrario, se genera un nombre por defecto.
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
    """Obtiene el nombre de un jugador dado su ID.

    Args:
        game: Objeto que contiene el estado del juego, debe tener atributo 'players'.
        player_id: Identificador único del jugador cuyo nombre se va a obtener.

    Returns:
        str: Nombre del jugador si se encuentra; de lo contrario, string por defecto
            en formato "Player {player_id}".
    """
    if not hasattr(game.state, "players") or not game.state.players:
        return f"Player {player_id}"

    for player in game.state.players:
        if player.id == player_id:
            return getattr(player, "name", f"Player {player_id}")

    return f"Player {player_id}"


def _get_term_limited_players(game):
    """Obtiene lista de jugadores restringidos de roles gubernamentales en la siguiente ronda.

    Args:
        game: Objeto que representa el estado actual del juego. Se espera que tenga
            un atributo 'state' que contiene información sobre el gobierno anterior
            y la lista de jugadores.

    Returns:
        list: Lista de diccionarios, cada uno representando un jugador con límite
            de términos con las siguientes claves:
            - "id": Identificador único del jugador.
            - "name": Nombre del jugador (o nombre por defecto si no está disponible).
            - "reason": Razón del límite ("former_chancellor" o "former_president_small_game").

    Note:
        - Si no hay gobierno anterior, retorna lista vacía.
        - El ex-canciller siempre tiene límite de términos.
        - En juegos con 5 o menos jugadores, el ex-presidente también tiene límite.
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
    """Obtiene un objeto jugador del estado del juego por su ID único.

    Args:
        game: Objeto que representa el juego actual, se espera que tenga un
            atributo 'state' con una lista 'players'.
        player_id: Identificador único del jugador a obtener.

    Returns:
        Player: Objeto jugador con el ID coincidente si se encuentra; de lo contrario, None.
    """
    if not hasattr(game.state, "players") or not game.state.players:
        return None

    for player in game.state.players:
        if player.id == player_id:
            return player

    return None


def _get_nomination_info(game):
    """Obtiene información de nominación para el estado actual del juego.

    Esta función recopila detalles sobre la fase actual de nominación, incluyendo
    los candidatos a canciller elegibles, el candidato actual a canciller (si existe),
    y si el juego está en fase de votación. Usa el método de estado de juego mejorado
    get_eligible_chancellors() si está disponible para determinar candidatos elegibles.

    Args:
        game: Instancia del juego que contiene el estado actual.

    Returns:
        dict: Diccionario con las siguientes claves:
            - "chancellorCandidate": Información sobre candidato actual a canciller (dict o None).
            - "eligibleChancellors": Lista de candidatos elegibles a canciller, cada uno
              como dict con 'id', 'name', e 'isTermLimited'.
            - "isVotingPhase": Boolean indicando si el juego está actualmente en fase de votación.
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
    """Extrae información de contadores del objeto juego dado.

    Esta función inspecciona el objeto game.state para atributos específicos
    de contadores y retorna sus valores en un diccionario. Si un atributo
    no está presente, se usa un valor por defecto.

    Args:
        game: Objeto que representa el estado actual del juego, se espera que
            tenga un atributo 'state'.

    Returns:
        dict: Diccionario que contiene las siguientes claves:
            - "electionTracker": Valor actual del contador de elecciones (por defecto: 0).
            - "roundNumber": Número de ronda actual (por defecto: 1).
            - "enactedPolicies": Lista o conteo de políticas promulgadas, si está presente.
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
    """Obtiene el estado actual del tablero del juego.

    Esta función extrae y retorna información sobre el estado del tablero,
    incluyendo el número de políticas promulgadas para cada facción, el número
    de cartas de política en el mazo y pila de descarte, si el poder de veto está
    disponible, y los poderes disponibles para facciones fascista y comunista.

    Args:
        game: Instancia del juego que contiene el estado actual y tablero.

    Returns:
        dict: Diccionario con las siguientes claves:
            - "liberalPolicies" (int): Número de políticas liberales promulgadas.
            - "fascistPolicies" (int): Número de políticas fascistas promulgadas.
            - "communistPolicies" (int): Número de políticas comunistas promulgadas.
            - "policiesInDeck" (int): Número de cartas restantes en el mazo.
            - "policiesInDiscard" (int): Número de cartas en la pila de descarte.
            - "vetoAvailable" (bool): Si el poder de veto está actualmente disponible.
            - "powers" (dict): Información sobre poderes disponibles para facciones.
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
    """Obtiene lista de diccionarios con información sobre poderes fascistas en el tablero.

    Cada diccionario en la lista retornada incluye:
    - position (int): Posición basada en 1 del poder en la pista fascista.
    - power (Any): El poder en esta posición.
    - isActive (bool): Si el poder está actualmente activo, basado en la pista fascista del tablero.
    - description (str): Descripción textual del poder, o "No power" si no hay.

    Args:
        board: Objeto tablero, se espera que tenga 'fascist_powers' (iterable)
            y opcionalmente 'fascist_track' (int).

    Returns:
        list[dict]: Lista de diccionarios de información de poderes fascistas.
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
    """Recopila información sobre los poderes comunistas presentes en el tablero dado.

    Itera a través del atributo 'communist_powers' del tablero, si existe, y construye
    una lista de diccionarios que contienen detalles para cada poder, incluyendo su
    posición, nombre, estado de activación y descripción.

    Args:
        board: Objeto que representa el tablero del juego, se espera que tenga
            atributos 'communist_powers' (lista) y opcionalmente 'communist_track' (int).

    Returns:
        list[dict]: Lista de diccionarios, cada uno conteniendo:
            - "position" (int): Índice basado en 1 del poder.
            - "power" (Any): El poder en sí.
            - "isActive" (bool): Si el poder está actualmente activo basado en la pista comunista.
            - "description" (str): Descripción del poder, o "No power" si no está presente.
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
    """Infiere y retorna información sobre la última acción significativa en el juego.

    El diccionario retornado contiene:
    - type (str): Tipo de la última acción ('policy_enacted', 'game_started', 'initialization', 'error').
    - player (dict o None): Información sobre el jugador involucrado, incluyendo 'id' y 'name'.
    - description (str): Descripción legible de la última acción.
    - timestamp (str): Timestamp de cuando se infirió la acción.

    La función intenta:
    - Determinar si se promulgó una política y por quién, usando el gobierno anterior
      o canciller actual como respaldo.
    - Identificar el tipo de política promulgada (fascista, liberal o comunista).
    - Manejar casos donde el juego acaba de comenzar o se está inicializando.
    - Manejar errores graciosamente y retornar acción de error si es necesario.

    Args:
        game: Objeto del juego que contiene el estado actual e información del tablero.

    Returns:
        dict: Diccionario con detalles sobre la última acción.
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
