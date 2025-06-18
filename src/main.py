import argparse
from random import seed

from src.game.game import SHXLGame
from src.game.game_logger import GameLogger, LogLevel


def run_game(
    players,
    with_communists=True,
    with_anti_policies=False,
    with_emergency_powers=False,
    strategy="role",
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


def get_player_and_human_config():
    """Get player count and human player configuration"""
    # Player count
    while True:
        try:
            player_count = int(input("Number of players (6-16): "))
            if 6 <= player_count <= 16:
                break
            print("Please enter a number between 6 and 16.")
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

    return player_count, human_players


def select_game_mode():
    """Select game mode and return configuration"""
    print("\n===== Secret Hitler XL - Game Mode Selection =====\n")
    print("Select game mode:")
    print("  1. Classic Mode (Original Secret Hitler)")
    print("  2. XL Mode (Full Secret Hitler XL experience)")
    print("  3. Personalized (Custom configuration)")

    while True:
        try:
            mode_choice = int(input("\nEnter choice (1-3): "))
            if 1 <= mode_choice <= 3:
                break
            print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")

    if mode_choice == 1:
        # Classic Mode
        print("\n=== Classic Mode Selected ===")
        print(
            "Configuration: No communists, no anti-policies, no emergency powers, role-based AI"
        )

        player_count, human_players = get_player_and_human_config()

        return {
            "player_count": player_count,
            "with_communists": False,
            "with_anti_policies": False,
            "with_emergency_powers": False,
            "strategy": "role",
            "human_players": human_players,
        }

    elif mode_choice == 2:
        # XL Mode
        print("\n=== XL Mode Selected ===")
        print("Configuration: Communists, anti-policies, emergency powers, smart AI")

        player_count, human_players = get_player_and_human_config()

        return {
            "player_count": player_count,
            "with_communists": True,
            "with_anti_policies": True,
            "with_emergency_powers": True,
            "strategy": "role",
            "human_players": human_players,
        }

    else:
        # Personalized Mode
        print("\n=== Personalized Mode Selected ===")
        return personalized_setup()


def personalized_setup():
    """Personalized setup for game parameters (original interactive_setup logic)"""
    player_count, human_players = get_player_and_human_config()

    # Communist faction
    while True:
        communist_choice = input("\nInclude communist faction? (y/n): ").lower()
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

    return {
        "player_count": player_count,
        "with_communists": with_communists,
        "with_anti_policies": with_anti_policies,
        "with_emergency_powers": with_emergency_powers,
        "strategy": strategy,
        "human_players": human_players,
    }


def ask_play_again():
    """Ask the user if they want to play again"""
    while True:
        choice = input("\nWould you like to play another game? (y/n): ").lower().strip()
        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def run_game_loop(config, logger):
    """Run games in a loop until the user chooses to exit"""
    game_number = 1

    # Welcome message for the first game
    print("\n" + "=" * 60)
    print("           WELCOME TO SECRET HITLER XL!")
    print("=" * 60)

    while True:
        # Clear visual separator for new game
        if game_number > 1:
            print("\n" + "=" * 60)
            print(f"                    GAME #{game_number}")
            print("=" * 60)
        else:
            print(f"\n                    GAME #{game_number}")
            print("=" * 60)

        # Show configuration summary
        print_configuration_summary(config)

        # Run the game
        print("Starting game...\n")
        run_game(
            config["player_count"],
            with_communists=config["with_communists"],
            with_anti_policies=config["with_anti_policies"],
            with_emergency_powers=config["with_emergency_powers"],
            strategy=config["strategy"],
            human_players=config["human_players"],
            logger=logger,
        )

        # Game finished
        print("\n" + "=" * 60)
        print(f"                 GAME #{game_number} FINISHED")
        print("=" * 60)

        # Ask if they want to play again
        if not ask_play_again():
            print("\nThanks for playing Secret Hitler XL! Goodbye!")
            break

        # Ask if they want to change configuration for next game
        print("\nPreparing for a new game...")
        while True:
            change_config = (
                input("Do you want to change the game configuration? (y/n): ")
                .lower()
                .strip()
            )
            if change_config in ("y", "yes"):
                config = interactive_setup()
                break
            elif change_config in ("n", "no"):
                print("Using the same configuration for the next game.")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")

        game_number += 1


def print_configuration_summary(config):
    """Print a summary of the game configuration"""
    print("\n=== Game Configuration Summary ===")
    print(f"Players: {config['player_count']}")
    print(
        f"Communist Faction: {'Enabled' if config['with_communists'] else 'Disabled'}"
    )
    print(f"Anti-policies: {'Enabled' if config['with_anti_policies'] else 'Disabled'}")
    print(
        f"Emergency Powers: {'Enabled' if config['with_emergency_powers'] else 'Disabled'}"
    )
    print(f"AI Strategy: {config['strategy'].capitalize()}")
    print(
        f"Human Players: {config['human_players'] if config['human_players'] else 'None'}"
    )
    print("==============================\n")


def interactive_setup():
    """Interactive setup for game parameters"""
    return select_game_mode()


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
        default="role",
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

    cli_logger = GameLogger(
        selected_level
    )  # Determine if we should use interactive setup

    use_interactive = args.interactive or args.players is None

    if use_interactive:

        # Use interactive setup and game loop

        config = interactive_setup()

        # Run games in a loop
        run_game_loop(config, cli_logger)

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

        run_game(
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
