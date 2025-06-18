"""
Game management business logic
"""

import uuid

from flask import jsonify

from src.game.game import SHXLGame
from src.players.player_factory import PlayerFactory

from ..storage import games
from ..utils.game_state_helpers import (
    _get_board_info,
    _get_current_phase_info,
    _get_current_timestamp,
    _get_game_config_info,
    _get_game_state_status,
    _get_government_info,
    _get_last_action_info,
    _get_nomination_info,
    _get_players_info,
    _get_trackers_info,
)


def create_new_game_handler(data):
    """Handle new game creation"""
    if not data:
        data = {}

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


def join_game_handler(game_id, data):
    """Handle player joining game"""
    if not data:
        return jsonify({"error": "Missing request body"}), 400

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


def start_game_handler(game_id, data):
    """Handle game start"""
    if not data:
        return jsonify({"error": "Missing request body"}), 400

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


def add_bots_handler(game_id, data):
    """Handle adding bots to game"""
    if not data:
        data = {}

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


def get_game_state_handler(game_id, requesting_player_id=None):
    """Handle game state retrieval"""
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

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
