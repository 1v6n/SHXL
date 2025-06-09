# Secret Hitler XL

A Python implementation of the Secret Hitler XL game, a variant of the popular Secret Hitler game with additional mechanics including a communist faction.

## Overview

This implementation provides a complete, object-oriented implementation of the Secret Hitler XL game, following the rules from the Secret Hitler XL Handbook. It supports 6-16 players, includes communists, anti-policies, and emergency powers, and uses proper design patterns to create a flexible, maintainable codebase.

## Features

- Support for 6-16 players
- Communist faction in addition to Liberals and Fascists
- Policy trackers with presidential powers
- Anti-policies and emergency powers
- All game mechanics from the Secret Hitler XL Handbook
- AI players with different strategies
- Comprehensive logging for game events

## Design Patterns

The implementation uses several design patterns:

- **Factory Pattern**: Used for roles, policies, and players, allowing easy creation of these objects.
- **Strategy Pattern**: Used for AI player behaviors, allowing different strategies to be plugged in.
- **State Pattern**: Used for game phases, allowing the game to transition smoothly between different phases.
- **Command Pattern**: Used for presidential powers, encapsulating each power as a separate command.

## Project Structure

- `src/`: Source code
  - `board/`: Game board and state tracking
  - `game/`: Main game logic and phases
  - `players/`: Player implementations including AI
  - `policies/`: Policy implementations
  - `roles/`: Role implementations
- `tests/`: Unit tests
- `features/`: Cucumber feature files for behavior-driven testing
  - `steps/`: Cucumber test step implementations

## Running the Game

To run the game:

```bash
python src/main.py --players 8 --strategy random
```

Command-line options:

- `--players`: Number of players (6-16)
- `--no-communists`: Disable communist faction
- `--anti-policies`: Enable anti-policies
- `--emergency-powers`: Enable emergency powers
- `--strategy`: AI strategy (random, role, smart)
- `--seed`: Random seed for reproducibility

## Running Tests

To run the unit tests:

```bash
python -m unittest discover -s tests
```

Or use the makefile:

```bash
make test
```

To run Cucumber/Behave tests:

```bash
python -m behave
```

Or use the makefile:

```bash
make cucumber
```

To run all tests:

```bash
make all-tests
```

For more information about the Cucumber tests, see [docs/cucumber_tests.md](docs/cucumber_tests.md).

## Future Enhancements

1. Integration with a user interface
2. Improved AI strategies
3. Network play
4. Game statistics and analysis

## License

[MIT License](LICENSE)
