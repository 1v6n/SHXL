import argparse
from random import seed

from src.game.game import SHXLGame
from src.game.game_logger import GameLogger, LogLevel
from src.players.player_factory import PlayerFactory


def run_game(
    players,
    with_communists=True,
    with_anti_policies=False,
    with_emergency_powers=False,
    strategy="smart",
    human_players=None,
    logger=None,  # add logger parameter
):
    """

    Run a game of Secret Hitler XL with the given parameters



    Args:

        players (int): Number of players (6-16)

        with_communists (bool): Whether to include communists

        with_anti_policies (bool): Whether to include anti-policies

        with_emergency_powers (bool): Whether to include emergency powers

        strategy (str): Strategy type for AI players ("random", "role", "smart")

        human_players (list): List of player IDs that should be human-controlled



    Returns:

        str: Game result

    """

    # Validate player count

    if players < 6 or players > 16:

        raise ValueError("Player count must be between 6 and 16")

    game = SHXLGame(logger=logger)  # Set up the game

    game.setup_game(
        players,
        with_communists=with_communists,
        with_anti_policies=with_anti_policies,
        with_emergency_powers=with_emergency_powers,
        human_player_indices=human_players,
        ai_strategy=strategy,
    )

    # Run the game

    result = game.start_game()

    return result


def interactive_setup():
    """Interactive setup for game parameters"""

    print("\n===== Secret Hitler XL - Game Setup =====\n")

    # Player count

    while True:

        try:

            player_count = int(input("Number of players (6-16): "))

            if 6 <= player_count <= 16:

                break

            print("Please enter a number between 6 and 16.")

        except ValueError:

            print("Please enter a valid number.")

    # Communist faction

    while True:

        communist_choice = input("Include communist faction? (y/n): ").lower()

        if communist_choice in ("y", "n"):

            with_communists = communist_choice == "y"

            break

        print("Please enter 'y' or 'n'.")

    # Anti-policies (only if communists are enabled)

    with_anti_policies = False

    if with_communists:

        while True:

            anti_policies_choice = input("Include anti-policies? (y/n): ").lower()

            if anti_policies_choice in ("y", "n"):

                with_anti_policies = anti_policies_choice == "y"

                break

            print("Please enter 'y' or 'n'.")

    # Emergency powers

    while True:

        emergency_powers_choice = input("Include emergency powers? (y/n): ").lower()

        if emergency_powers_choice in ("y", "n"):

            with_emergency_powers = emergency_powers_choice == "y"

            break

        print("Please enter 'y' or 'n'.")

    # AI strategy

    strategies = ["random", "role", "smart"]

    print("\nSelect AI strategy:")

    print("  1. Random (AI makes completely random choices)")

    print("  2. Role (AI makes role-based decisions)")

    print("  3. Smart (AI uses advanced strategy)")

    while True:

        try:

            strategy_choice = int(input("Enter choice (1-3): "))

            if 1 <= strategy_choice <= 3:

                strategy = strategies[strategy_choice - 1]

                break

            print("Please enter a number between 1 and 3.")

        except ValueError:

            print("Please enter a valid number.")

    # Human players

    human_players = []

    while True:

        try:

            human_count = int(input(f"\nHow many human players? (0-{player_count}): "))

            if 0 <= human_count <= player_count:

                break

            print(f"Please enter a number between 0 and {player_count}.")

        except ValueError:

            print("Please enter a valid number.")

    for i in range(human_count):

        while True:

            try:

                player_id = int(
                    input(f"Enter human player {i+1} ID (0-{player_count-1}): ")
                )

                if 0 <= player_id < player_count and player_id not in human_players:

                    human_players.append(player_id)

                    break

                elif player_id in human_players:

                    print("This player ID is already assigned. Please choose another.")

                else:

                    print(f"Please enter a number between 0 and {player_count-1}.")

            except ValueError:

                print("Please enter a valid number.")

    # Random seed

    seed_value = None

    while True:

        seed_choice = input(
            "\nUse a specific random seed for reproducibility? (y/n): "
        ).lower()

        if seed_choice in ("y", "n"):

            if seed_choice == "y":

                while True:

                    try:

                        seed_value = int(input("Enter seed value: "))

                        break

                    except ValueError:

                        print("Please enter a valid number.")

            break

        print("Please enter 'y' or 'n'.")

    if seed_value is not None:

        seed(seed_value)

    print("\n=== Game Configuration Summary ===")

    print(f"Players: {player_count}")

    print(f"Communist Faction: {'Enabled' if with_communists else 'Disabled'}")

    print(f"Anti-policies: {'Enabled' if with_anti_policies else 'Disabled'}")

    print(f"Emergency Powers: {'Enabled' if with_emergency_powers else 'Disabled'}")

    print(f"AI Strategy: {strategy.capitalize()}")

    print(f"Human Players: {human_players if human_players else 'None'}")

    print(f"Random Seed: {seed_value if seed_value is not None else 'Random'}")

    print("==============================\n")

    return {
        "player_count": player_count,
        "with_communists": with_communists,
        "with_anti_policies": with_anti_policies,
        "with_emergency_powers": with_emergency_powers,
        "strategy": strategy,
        "human_players": human_players,
    }


def main():
    """Main entry point for the game"""

    # Parse command line arguments

    parser = argparse.ArgumentParser(description="Run a game of Secret Hitler XL")

    parser.add_argument(
        "--players", type=int, default=None, help="Number of players (6-16)"
    )

    parser.add_argument(
        "--no-communists", action="store_true", help="Disable communist faction"
    )

    parser.add_argument(
        "--anti-policies", action="store_true", help="Enable anti-policies"
    )

    parser.add_argument(
        "--emergency-powers", action="store_true", help="Enable emergency powers"
    )

    parser.add_argument(
        "--strategy",
        type=str,
        default="smart",
        choices=["random", "role", "smart"],
        help="AI strategy type",
    )

    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )

    parser.add_argument(
        "--human-player",
        type=int,
        default=None,
        help="ID of the human player (0 to player_count-1)",
    )

    parser.add_argument(
        "--human-players",
        type=str,
        default=None,
        help='Comma-separated list of human player IDs (e.g., "0,2,5")',
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=[l.name.lower() for l in LogLevel],
        default="normal",
        help="Logging level",
    )

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Use interactive setup"
    )

    args = parser.parse_args()

    # build logger from CLI arg

    selected_level = LogLevel[args.log_level.upper()]

    cli_logger = GameLogger(selected_level)

    # Determine if we should use interactive setup

    use_interactive = args.interactive or args.players is None

    if use_interactive:

        # Use interactive setup

        config = interactive_setup()

        # Run the game with interactive parameters

        result = run_game(
            config["player_count"],
            with_communists=config["with_communists"],
            with_anti_policies=config["with_anti_policies"],
            with_emergency_powers=config["with_emergency_powers"],
            strategy=config["strategy"],
            human_players=config["human_players"],
            logger=cli_logger,
        )

    else:

        # Use command-line arguments

        # Set random seed if provided

        if args.seed is not None:

            seed(args.seed)

        # Process human player IDs

        human_players = []

        if args.human_player is not None:

            human_players.append(args.human_player)

        if args.human_players:

            human_players.extend(
                [
                    int(pid.strip())
                    for pid in args.human_players.split(",")
                    if pid.strip()
                ]
            )

        human_players = list(set(human_players))

        result = run_game(
            args.players if args.players else 8,  # Default to 8 players
            with_communists=not args.no_communists,
            with_anti_policies=args.anti_policies,
            with_emergency_powers=args.emergency_powers,
            strategy=args.strategy,
            human_players=human_players,
            logger=cli_logger,
        )


if __name__ == "__main__":

    main()
