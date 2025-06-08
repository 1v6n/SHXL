import uuid

from flask import Flask, jsonify, request

from src.game.game import SHXLGame
from src.players.player_factory import PlayerFactory

app = Flask(__name__)
games = {}


@app.route("/newgame", methods=["POST"])
def create_new_game():
    data = request.json
    player_count = data.get("playerCount", 10)
    include_communists = data.get("withCommunists", True)
    with_anti_policies = data.get("withAntiPolicies", True)
    with_emergency_powers = data.get("withEmergencyPowers", True)
    strategy = data.get("strategy", "smart")

    game_id = str(uuid.uuid4())[:8]
    game = SHXLGame()
    game.setup_game(
        player_count,
        include_communists,
        with_anti_policies,
        with_emergency_powers,
        ai_strategy=strategy,
    )

    games[game_id] = game

    return (
        jsonify(
            {
                "gameID": game_id,
                "hostPlayerID": game.state.players[0].id,
                "maxPlayers": player_count,
                "state": "waiting_for_players",
            }
        ),
        201,
    )


@app.route("/games/<game_id>/join", methods=["POST"])
def join_game(game_id):
    data = request.get_json()
    player_name = data.get("playerName")

    if not player_name:
        return jsonify({"error": "Missing playerName"}), 400

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if game.state.game_started:
        return jsonify({"error": "Game already in progress"}), 403

    if len(game.state.players) >= game.player_count:
        return jsonify({"error": "Game is full"}), 403

    # Crear jugador humano
    new_id = len(game.state.players)
    player = game.state.player_factory.create_single_player(
        player_id=new_id, name=player_name, is_human=True
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


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK", "message": "Server is running"}), 200


if __name__ == "__main__":
    app.run(debug=True)
