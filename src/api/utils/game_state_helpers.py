"""
Game state helper functions extracted from original app.py
"""

import datetime


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


def _get_players_info(game, requesting_player_id=None):
    """Get player information with proper role visibility - using logger logic"""
    players_info = []

    for player in game.state.players:
        player_info = {
            "id": getattr(player, "id", -1),
            "name": getattr(player, "name", f"Player {getattr(player, 'id', '?')}"),
            "position": getattr(player, "id", -1),
            "isAlive": getattr(player, "is_alive", True),
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
