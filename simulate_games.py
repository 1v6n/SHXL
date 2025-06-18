"""Simulador de partidas para Secret Hitler XL.

Este módulo permite ejecutar múltiples simulaciones del juego Secret Hitler XL
para analizar estadísticas y balanceo del juego con diferentes configuraciones.
"""

import argparse
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt  # type: ignore[import-not-found]

from src.game.game import SHXLGame

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def get_simulation_config():
    """Obtiene la configuración de simulación de forma interactiva.

    Returns:
        dict: Diccionario con la configuración de simulación seleccionada.
    """
    print("\n===== Secret Hitler XL - Simulation Configuration =====\n")

    while True:
        try:
            n_games = int(input("Number of games to simulate (default 100): ") or "100")
            if n_games > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        try:
            player_count = int(input("Number of players (6-16, default 10): ") or "10")
            if 6 <= player_count <= 16:
                break
            print("Please enter a number between 6 and 16.")
        except ValueError:
            print("Please enter a valid number.")

    while True:
        communist_choice = (
            input("Include communist faction? (y/n, default y): ").lower() or "y"
        )
        if communist_choice in ("y", "n"):
            with_communists = communist_choice == "y"
            break
        print("Please enter 'y' or 'n'.")

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

    while True:
        emergency_powers_choice = (
            input("Include emergency powers? (y/n, default n): ").lower() or "n"
        )
        if emergency_powers_choice in ("y", "n"):
            with_emergency_powers = emergency_powers_choice == "y"
            break
        print("Please enter 'y' or 'n'.")

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
    """Imprime un resumen de la configuración de simulación.

    Args:
        config (dict): Diccionario con la configuración de simulación.
    """
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
    """Simulador para ejecutar múltiples partidas del juego y analizar estadísticas.

    Esta clase gestiona la ejecución de simulaciones del juego, recopila estadísticas
    y genera visualizaciones de los resultados.
    """

    def __init__(self):
        """Inicializa el simulador con estructuras de datos vacías para estadísticas."""
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
        """Ejecuta una sola partida del juego y recopila estadísticas.

        Args:
            player_count (int): Número de jugadores.
            with_communists (bool): Si incluir facción comunista.
            with_anti_policies (bool): Si incluir anti-políticas.
            with_emergency_powers (bool): Si incluir poderes de emergencia.
            strategy_type (str): Tipo de estrategia para jugadores IA.

        Returns:
            dict: Diccionario con estadísticas de la partida.
        """
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
        """Procesa el resultado de una partida individual.

        Args:
            result (dict): Resultado de una partida individual.
        """
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
        """Ejecuta múltiples simulaciones del juego.

        Args:
            n_games (int): Número de partidas a simular.
            player_count (int): Número de jugadores por partida.
            with_communists (bool): Si incluir facción comunista.
            with_anti_policies (bool): Si incluir anti-políticas.
            with_emergency_powers (bool): Si incluir poderes de emergencia.
            strategy_type (str): Tipo de estrategia para jugadores IA.
            parallel (bool): Si ejecutar en paralelo.

        Returns:
            dict: Diccionario con estadísticas agregadas de todas las partidas.
        """
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
        """Genera estadísticas agregadas de las simulaciones.

        Args:
            n_games (int): Número total de partidas simuladas.
            elapsed (float): Tiempo transcurrido en segundos.

        Returns:
            dict: Diccionario con estadísticas agregadas.
        """
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

    def print_detailed_results(self, stats):
        """Imprime resultados detallados de la simulación en CLI.

        Args:
            stats (dict): Diccionario con estadísticas de simulación.
        """
        print("\n" + "=" * 60)
        print("            SIMULATION RESULTS")
        print("=" * 60)

        print(f"\nTotal Games Played: {stats['total_games']}")
        print(f"Average Game Length: {stats['avg_rounds']:.2f} rounds")
        print(f"Total Simulation Time: {stats['elapsed']:.2f} seconds")
        print(
            f"Average Time per Game: {stats['elapsed']/stats['total_games']:.3f} seconds"
        )

        print("\n" + "-" * 40)
        print("           WIN STATISTICS")
        print("-" * 40)

        total_wins = sum(stats["win_counts"].values())
        for faction, count in sorted(stats["win_counts"].items()):
            percentage = (count / total_wins) * 100 if total_wins > 0 else 0
            bar_length = int(percentage / 2)  # Scale bar to fit in terminal
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(
                f"{faction.capitalize():>12}: {count:>4} wins ({percentage:>6.2f}%) {bar}"
            )

        print("\n" + "-" * 40)
        print("        POLICY DISTRIBUTION")
        print("-" * 40)

        policy_total = sum(stats["policy_distribution"].values())
        for policy_type, percentage in sorted(stats["policy_distribution"].items()):
            count = int(percentage * policy_total)
            bar_length = int(percentage * 50)  # Scale bar to fit in terminal
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"{policy_type.capitalize():>12}: {percentage:>6.2f}% {bar}")

        print("\n" + "=" * 60)

    def plot_results(self, stats):
        """Genera gráficos de los resultados de simulación.

        Args:
            stats (dict): Diccionario con estadísticas de simulación.
        """
        # First print detailed CLI results
        self.print_detailed_results(stats)

        # Then optionally generate graphs
        try:
            fig, axs = plt.subplots(1, 2, figsize=(12, 5))

            # Win rates
            axs[0].bar(
                stats["win_rates"].keys(),
                [v * 100 for v in stats["win_rates"].values()],
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
            print(f"\nGraphs saved as 'simulation_results.png'")
            plt.show()
        except Exception as e:
            print(f"\nNote: Could not generate graphs: {e}")
            print("This might be due to missing matplotlib or display issues.")

    def print_strategy_comparison(self, strategy_results):
        """Imprime comparación detallada entre estrategias en CLI.

        Args:
            strategy_results (dict): Diccionario con resultados por estrategia.
        """
        print("\n" + "=" * 80)
        print("                    STRATEGY COMPARISON RESULTS")
        print("=" * 80)

        # Print overall summary
        strategies = list(strategy_results.keys())
        print(f"\nStrategies compared: {', '.join(strategies)}")

        # Print win rates comparison
        print("\n" + "-" * 50)
        print("              WIN RATES BY STRATEGY")
        print("-" * 50)  # Get all factions from all strategies
        all_factions = set()
        for stats in strategy_results.values():
            all_factions.update(stats["win_counts"].keys())

        # Define faction order for consistent display
        faction_order = ["liberal", "fascist", "communist"]
        ordered_factions = [f for f in faction_order if f in all_factions]
        # Add any other factions that might exist
        ordered_factions.extend(
            [f for f in sorted(all_factions) if f not in faction_order]
        )

        for faction in ordered_factions:
            print(f"\n{faction.upper()} FACTION:")
            for strategy in strategies:
                stats = strategy_results[strategy]
                total_games = sum(stats["win_counts"].values())
                wins = stats["win_counts"].get(faction, 0)
                percentage = (wins / total_games) * 100 if total_games > 0 else 0
                bar_length = int(percentage / 2)  # Scale bar to fit in terminal
                bar = "█" * bar_length + "░" * (50 - bar_length)
                print(f"  {strategy:>10}: {wins:>4} wins ({percentage:>6.2f}%) {bar}")

        # Print game length comparison
        print("\n" + "-" * 50)
        print("           AVERAGE GAME LENGTH")
        print("-" * 50)

        for strategy in strategies:
            avg_rounds = strategy_results[strategy]["avg_rounds"]
            elapsed = strategy_results[strategy]["elapsed"]
            total_games = strategy_results[strategy]["total_games"]
            print(
                f"{strategy:>10}: {avg_rounds:>6.2f} rounds avg | {elapsed:>6.2f}s total | {elapsed/total_games:>6.3f}s per game"
            )

        print("\n" + "=" * 80)

    def plot_comparison(self, strategy_results):
        """Genera gráficos de comparación entre estrategias.

        Args:
            strategy_results (dict): Diccionario con resultados por estrategia.
        """
        # First print detailed CLI results
        self.print_strategy_comparison(strategy_results)

        # Then optionally generate graphs
        try:
            fig, axs = plt.subplots(1, 2, figsize=(12, 5))

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

            strategies = list(strategy_results.keys())
            avg_rounds = [strategy_results[s]["avg_rounds"] for s in strategies]
            axs[1].bar(strategies, avg_rounds)
            axs[1].set_title("Average Game Length")
            axs[1].set_ylabel("Rounds")

            plt.tight_layout()
            plt.savefig("strategy_comparison.png")
            print(f"\nStrategy comparison graphs saved as 'strategy_comparison.png'")
            plt.show()
        except Exception as e:
            print(f"\nNote: Could not generate graphs: {e}")
            print("This might be due to missing matplotlib or display issues.")

    def compare_strategies(self, strategies, **kwargs):
        """Compara múltiples estrategias ejecutando simulaciones para cada una.

        Args:
            strategies (list): Lista de estrategias a comparar.
            **kwargs: Argumentos adicionales para las simulaciones.
        """
        results = {}
        for strategy in strategies:
            print(
                f"\nRunning {kwargs.get('n_games', 100)} games with {strategy} strategy..."
            )
            stats = self.run_simulations(strategy_type=strategy, **kwargs)
            results[strategy] = stats

        self.plot_comparison(results)


def main():
    """Función principal del simulador.

    Maneja argumentos de línea de comandos y ejecuta simulaciones según
    la configuración especificada.
    """
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

    use_interactive = args.interactive

    if use_interactive:
        config = get_simulation_config()
        print_simulation_summary(config)

        sim = GameSimulator()

        if config["compare_strategies"]:
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
            stats = sim.run_simulations(
                n_games=config["n_games"],
                player_count=config["player_count"],
                with_communists=config["with_communists"],
                with_anti_policies=config["with_anti_policies"],
                with_emergency_powers=config["with_emergency_powers"],
                strategy_type=config["strategy"],
                parallel=config["parallel"],
            )

            # The detailed results will be printed by plot_results method
            sim.plot_results(stats)

        return

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

    # The detailed results will be printed by plot_results method
    sim.plot_results(stats)


if __name__ == "__main__":
    main()
