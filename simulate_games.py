import argparse
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt  # type: ignore[import-not-found]

from src.game.game import SHXLGame

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def get_simulation_config():
    """Get simulation configuration interactively"""
    print("\n===== Secret Hitler XL - Simulation Configuration =====\n")

    # Number of games
    while True:
        try:
            n_games = int(input("Number of games to simulate (default 100): ") or "100")
            if n_games > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

    # Player count
    while True:
        try:
            player_count = int(input("Number of players (6-16, default 10): ") or "10")
            if 6 <= player_count <= 16:
                break
            print("Please enter a number between 6 and 16.")
        except ValueError:
            print("Please enter a valid number.")

    # Communist faction
    while True:
        communist_choice = (
            input("Include communist faction? (y/n, default y): ").lower() or "y"
        )
        if communist_choice in ("y", "n"):
            with_communists = communist_choice == "y"
            break
        print("Please enter 'y' or 'n'.")

    # Anti-policies (only if communists are enabled)
    with_anti_policies = False
    if with_communists:
        while True:
            anti_policies_choice = (
                input("Include anti-policies? (y/n, default n): ").lower() or "n"
            )
            if anti_policies_choice in ("y", "n"):
                with_anti_policies = anti_policies_choice == "y"
                break
            print("Please enter 'y' or 'n'.")

    # Emergency powers
    while True:
        emergency_powers_choice = (
            input("Include emergency powers? (y/n, default n): ").lower() or "n"
        )
        if emergency_powers_choice in ("y", "n"):
            with_emergency_powers = emergency_powers_choice == "y"
            break
        print("Please enter 'y' or 'n'.")

    # AI strategy or strategy comparison
    print("\nSelect simulation type:")
    print("  1. Single strategy simulation")
    print("  2. Strategy comparison")

    while True:
        try:
            sim_type = int(input("Enter choice (1-2, default 1): ") or "1")
            if sim_type in (1, 2):
                break
            print("Please enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")

    strategies = ["random", "role", "smart"]
    if sim_type == 1:
        # Single strategy
        print("\nSelect AI strategy:")
        print("  1. Random (AI makes completely random choices)")
        print("  2. Role (AI makes role-based decisions)")
        print("  3. Smart (AI uses advanced strategy)")

        while True:
            try:
                strategy_choice = int(input("Enter choice (1-3, default 2): ") or "2")
                if 1 <= strategy_choice <= 3:
                    strategy = strategies[strategy_choice - 1]
                    break
                print("Please enter a number between 1 and 3.")
            except ValueError:
                print("Please enter a valid number.")

        compare_strategies = None
    else:
        # Strategy comparison
        print("\nSelect strategies to compare (enter numbers separated by spaces):")
        print("  1. Random")
        print("  2. Role")
        print("  3. Smart")
        print("Example: '1 2 3' to compare all strategies")

        while True:
            try:
                choices = input("Enter strategy numbers (default '2 3'): ") or "2 3"
                strategy_indices = [int(x.strip()) - 1 for x in choices.split()]
                if (
                    all(0 <= i <= 2 for i in strategy_indices)
                    and len(strategy_indices) >= 2
                ):
                    compare_strategies = [strategies[i] for i in strategy_indices]
                    strategy = None
                    break
                print(
                    "Please enter valid strategy numbers (1-3), at least 2 strategies."
                )
            except ValueError:
                print("Please enter valid numbers separated by spaces.")

    # Parallel execution
    while True:
        parallel_choice = (
            input("Use parallel execution? (y/n, default y): ").lower() or "y"
        )
        if parallel_choice in ("y", "n"):
            parallel = parallel_choice == "y"
            break
        print("Please enter 'y' or 'n'.")

    return {
        "n_games": n_games,
        "player_count": player_count,
        "with_communists": with_communists,
        "with_anti_policies": with_anti_policies,
        "with_emergency_powers": with_emergency_powers,
        "strategy": strategy,
        "compare_strategies": compare_strategies,
        "parallel": parallel,
    }


def print_simulation_summary(config):
    """Print a summary of the simulation configuration"""
    print("\n=== Simulation Configuration Summary ===")
    print(f"Number of games: {config['n_games']}")
    print(f"Players per game: {config['player_count']}")
    print(
        f"Communist Faction: {'Enabled' if config['with_communists'] else 'Disabled'}"
    )
    print(f"Anti-policies: {'Enabled' if config['with_anti_policies'] else 'Disabled'}")
    print(
        f"Emergency Powers: {'Enabled' if config['with_emergency_powers'] else 'Disabled'}"
    )
    if config["compare_strategies"]:
        print(f"Strategy Comparison: {', '.join(config['compare_strategies'])}")
    else:
        print(f"AI Strategy: {config['strategy'].capitalize()}")
    print(f"Parallel Execution: {'Enabled' if config['parallel'] else 'Disabled'}")
    print("=========================================\n")


class GameSimulator:
    def __init__(self):
        self.results = []
        self.win_counts = Counter()
        self.victory_reasons = Counter()
        self.round_counts = []
        self.policy_counts = Counter()

    def run_single_game(
        self,
        player_count,
        with_communists=True,
        with_anti_policies=False,
        with_emergency_powers=False,
        strategy_type="role",
    ):
        from src.game.game_logger import GameLogger, LogLevel

        logger = GameLogger(LogLevel.NONE)  # Use no logging for simulations
        game = SHXLGame(logger)
        game.setup_game(
            player_count=player_count,
            with_communists=with_communists,
            with_anti_policies=with_anti_policies,
            with_emergency_powers=with_emergency_powers,
            ai_strategy=strategy_type,
        )
        winner = game.start_game()

        result = {
            "winner": winner,
            "rounds": game.state.round_number,
            "liberal": game.state.board.liberal_track,
            "fascist": game.state.board.fascist_track,
            "communist": game.state.board.communist_track if with_communists else 0,
        }
        return result

    def _process_result(self, result):
        self.results.append(result)
        winner = result["winner"]
        if winner == "liberal_and_communist" or winner == "liberals_and_communists":
            self.win_counts["liberal"] += 1
            self.win_counts["communist"] += 1
        else:
            self.win_counts[winner] += 1
        self.round_counts.append(result["rounds"])
        self.policy_counts["liberal"] += result["liberal"]
        self.policy_counts["fascist"] += result["fascist"]
        self.policy_counts["communist"] += result["communist"]

    def run_simulations(
        self,
        n_games=100,
        player_count=10,
        with_communists=True,
        with_anti_policies=False,
        with_emergency_powers=False,
        strategy_type="role",
        parallel=True,
    ):
        start = time.time()

        if parallel:
            with ProcessPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self.run_single_game,
                        player_count,
                        with_communists,
                        with_anti_policies,
                        with_emergency_powers,
                        strategy_type,
                    )
                    for _ in range(n_games)
                ]
                for future in futures:
                    self._process_result(future.result())
        else:
            for _ in range(n_games):
                result = self.run_single_game(
                    player_count,
                    with_communists,
                    with_anti_policies,
                    with_emergency_powers,
                    strategy_type,
                )
                self._process_result(result)

        elapsed = time.time() - start
        return self._generate_stats(n_games, elapsed)

    def _generate_stats(self, n_games, elapsed):
        total_wins = sum(self.win_counts.values())
        win_rates = {
            faction: count / total_wins if total_wins else 0
            for faction, count in self.win_counts.items()
        }
        policy_total = sum(self.policy_counts.values())
        policy_distribution = {
            key: val / policy_total for key, val in self.policy_counts.items()
        }
        return {
            "total_games": n_games,
            "elapsed": elapsed,
            "win_rates": win_rates,
            "avg_rounds": sum(self.round_counts) / len(self.round_counts),
            "policy_distribution": policy_distribution,
            "win_counts": dict(self.win_counts),
        }

    def plot_results(self, stats):
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))

        # Win rates
        axs[0].bar(
            stats["win_rates"].keys(), [v * 100 for v in stats["win_rates"].values()]
        )
        axs[0].set_title("Win Rates")
        axs[0].set_ylabel("%")

        # Policy distribution
        axs[1].pie(
            [v for v in stats["policy_distribution"].values()],
            labels=stats["policy_distribution"].keys(),
            autopct="%1.1f%%",
        )
        axs[1].set_title("Policy Distribution")

        plt.suptitle(
            f"{stats['total_games']} Games | Avg Rounds: {stats['avg_rounds']:.2f}"
        )
        plt.tight_layout()
        plt.savefig("simulation_results.png")
        plt.show()

    def plot_comparison(self, strategy_results):
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))

        # Win rate comparison
        for strategy, stats in strategy_results.items():
            total_games = sum(stats["win_counts"].values())
            factions = list(stats["win_counts"].keys())
            win_values = [
                (stats["win_counts"][f] / total_games) * 100 for f in factions
            ]
            axs[0].bar([f"{strategy}-{f}" for f in factions], win_values)
        axs[0].set_title("Win Rate by Strategy and Faction")
        axs[0].set_ylabel("Win Rate (%)")
        axs[0].tick_params(axis="x", rotation=45)

        # Average round length
        strategies = list(strategy_results.keys())
        avg_rounds = [strategy_results[s]["avg_rounds"] for s in strategies]
        axs[1].bar(strategies, avg_rounds)
        axs[1].set_title("Average Game Length")
        axs[1].set_ylabel("Rounds")

        plt.tight_layout()
        plt.savefig("strategy_comparison.png")
        plt.show()

    def compare_strategies(self, strategies, **kwargs):
        results = {}
        for strategy in strategies:
            print(f"\nRunning games with strategy: {strategy}")
            stats = self.run_simulations(strategy_type=strategy, **kwargs)
            results[strategy] = stats

            print("Win Rates:")
            for faction, rate in stats["win_rates"].items():
                print(f"  {faction}: {rate * 100:.2f}%")
            print(f"Average Rounds: {stats['avg_rounds']:.2f}")
            print(f"Elapsed Time: {stats['elapsed']:.2f} seconds")

        self.plot_comparison(results)


def main():
    parser = argparse.ArgumentParser(description="Run simulations of Secret Hitler XL")
    parser.add_argument("-n", "--num", type=int, default=100)
    parser.add_argument("-p", "--players", type=int, default=10)
    parser.add_argument("--no-communists", action="store_true")
    parser.add_argument("--anti-policies", action="store_true")
    parser.add_argument("--emergency-powers", action="store_true")
    parser.add_argument(
        "--strategy", default="role", choices=["smart", "role", "random"]
    )
    parser.add_argument("--sequential", action="store_true")
    parser.add_argument(
        "--compare",
        nargs="+",
        help="Compare multiple strategies (e.g. --compare smart random)",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Use interactive setup"
    )
    args = parser.parse_args()

    # Check if we should use interactive setup
    use_interactive = args.interactive

    if use_interactive:
        # Use interactive setup
        config = get_simulation_config()
        print_simulation_summary(config)

        sim = GameSimulator()

        if config["compare_strategies"]:
            # Strategy comparison
            sim.compare_strategies(
                strategies=config["compare_strategies"],
                n_games=config["n_games"],
                player_count=config["player_count"],
                with_communists=config["with_communists"],
                with_anti_policies=config["with_anti_policies"],
                with_emergency_powers=config["with_emergency_powers"],
                parallel=config["parallel"],
            )
        else:
            # Single strategy simulation
            stats = sim.run_simulations(
                n_games=config["n_games"],
                player_count=config["player_count"],
                with_communists=config["with_communists"],
                with_anti_policies=config["with_anti_policies"],
                with_emergency_powers=config["with_emergency_powers"],
                strategy_type=config["strategy"],
                parallel=config["parallel"],
            )

            print("\nResults:")
            for faction, rate in stats["win_rates"].items():
                print(f"- {faction.title()}: {rate*100:.2f}%")

            print(f"\nAverage Rounds: {stats['avg_rounds']:.2f}")
            print(f"Total Time: {stats['elapsed']:.2f} sec")

            sim.plot_results(stats)

        return

    # Use command-line arguments (existing logic)
    if args.compare:
        sim = GameSimulator()
        sim.compare_strategies(
            strategies=args.compare,
            n_games=args.num,
            player_count=args.players,
            with_communists=not args.no_communists,
            with_anti_policies=args.anti_policies,
            with_emergency_powers=args.emergency_powers,
            parallel=not args.sequential,
        )
        return

    sim = GameSimulator()
    stats = sim.run_simulations(
        n_games=args.num,
        player_count=args.players,
        with_communists=not args.no_communists,
        with_anti_policies=args.anti_policies,
        with_emergency_powers=args.emergency_powers,
        strategy_type=args.strategy,
        parallel=not args.sequential,
    )

    print("\nResults:")
    for faction, rate in stats["win_rates"].items():
        print(f"- {faction.title()}: {rate*100:.2f}%")

    print(f"\nAverage Rounds: {stats['avg_rounds']:.2f}")
    print(f"Total Time: {stats['elapsed']:.2f} sec")

    sim.plot_results(stats)


if __name__ == "__main__":
    main()
