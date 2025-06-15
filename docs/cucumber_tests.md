# Cucumber (Behave) Test Implementation

This document provides an overview of the implemented Cucumber tests using the Behave framework for Python.

## Overview

We have implemented Cucumber-style tests using the Behave framework to test the functionality of the Secret Hitler XL game. These tests are organized by features and scenarios as defined in the `.feature` files.

## Why BDD with Behave?

### Behavior-Driven Development Benefits

- **Human-Readable Specifications**: BDD allows us to write tests in natural language (Gherkin syntax) that stakeholders, developers, and testers can all understand. This creates a shared vocabulary for describing game behavior.

- **Living Documentation**: Feature files serve as both executable tests and up-to-date documentation of how the game should behave. When requirements change, the tests and documentation update together.

- **Domain-Focused Testing**: BDD encourages thinking about the game from the player's perspective rather than implementation details. This leads to better test coverage of actual user scenarios.

- **Collaboration**: Product owners, game designers, and developers can collaborate on writing scenarios, ensuring everyone understands the expected behavior.

### Why Behave Specifically?

- **Python Integration**: Behave integrates seamlessly with our Python codebase, allowing direct testing of game logic without translation layers.

- **Flexible Step Definitions**: Python's dynamic nature makes it easy to create reusable, parameterized step definitions that can handle various game scenarios.

- **Rich Ecosystem**: Behave works well with other Python testing tools like pytest, coverage, and mocking libraries.

- **CI/CD Integration**: Simple command-line interface that integrates easily with GitHub Actions and other CI systems.

## Integration Testing with BDD

### Testing Strategy

Our BDD tests function as **integration tests** by testing complete game workflows and interactions between components:

- **End-to-End Game Flows**: Tests like `game.feature` verify entire game sessions from initialization to completion, testing the interaction between phases, players, and game state.

- **Component Integration**: Features like `election_phase.feature` test how the election system integrates with player management, voting mechanisms, and state transitions.

- **System Boundaries**: Tests verify interactions between the game engine, player strategies, power systems, and board management.

### Implementation Approach

- **Realistic Game Scenarios**: Instead of testing individual methods in isolation, we test realistic game situations:

```gherkin
Scenario: Fascist government passes enabling act
  Given a game with 8 players including fascists
  And the fascist track has 3 policies enacted
  When a fascist president and fascist chancellor are elected
  And they enact a fascist policy
  Then the enabling act power should be triggered
  And the chancellor should be able to execute a player
```

- **State-Based Testing**: Tests verify that complex game state changes occur correctly across multiple components:

  - Player role assignments and hidden information
  - Policy deck management and shuffling
  - Power activation and execution
  - Win condition evaluation

- **Mock External Dependencies**: While testing integration between core components, we mock external dependencies like user input or random number generation for predictable tests:

```python
# In step definitions
@given("randint returns {value:d}")
def step_mock_randint(context, value):
    context.mock_randint.return_value = value
```

- **Cross-Component Validation**: Tests verify that changes in one system properly affect related systems:

  - Election outcomes affecting legislative phase setup
  - Policy enactment triggering appropriate powers
  - Player elimination updating game state and win conditions

### Testing Layers

- **Unit-like BDD Tests**: Some features test individual components in isolation (like `policy_deck.feature`) but still use business language.

- **Integration BDD Tests**: Most features test how multiple components work together (like `legislative_phase.feature` testing policy selection, enactment, and power activation).

- **System BDD Tests**: High-level features like `game.feature` test complete game workflows from start to finish.

This layered approach ensures we have both detailed component testing and broad system verification, all expressed in domain language that game designers can validate.

## Features Implemented

### Core Game Features

1. **Game Management** (`game.feature`, `game_managment.feature`, `start_game.feature`) - Tests the overall game flow, initialization, phase management, and game state transitions
2. **Game State** (`game_state.feature`) - Tests the game state management and data consistency
3. **Board Configuration** (`board.feature`) - Tests automatic board setup with policy tracks and powers based on player count and communist participation
4. **Setup Phase** (`setup_phase.feature`) - Tests game initialization, role distribution, and initial configuration

### Game Phases

1. **Election Phase** (`election_phase.feature`) - Tests the election mechanics including president rotation, chancellor nomination, term limits, voting, and election tracker
2. **Legislative Phase** (`legislative_phase.feature`) - Tests the policy selection and enactment process, including veto powers and deck management
3. **Game Over Phase** (`gameover_phase.feature`) - Tests end game conditions and victory determination

### Player Systems

1. **Abstract Player** (`abstract_player.feature`) - Tests the base player interface and common functionality
2. **Human Player** (`human_player.feature`) - Tests human player interactions through console input/output
3. **AI Player** (`ai_player.feature`) - Tests AI player decision-making and automated gameplay
4. **Player Factory** (`player_factory.feature`) - Tests player creation and instantiation

### Strategy Systems

1. **Base Strategy** (`base_strategy.feature`) - Tests the abstract strategy pattern implementation
2. **Liberal Strategy** (`liberal_strategy.feature`) - Tests liberal player AI behavior and decision-making
3. **Fascist Strategy** (`fascist_strategy.feature`) - Tests fascist player AI behavior including Hitler protection
4. **Communist Strategy** (`comunist_strategy.feature`) - Tests communist player AI behavior and strategic decisions
5. **Random Strategy** (`random_strategy.feature`) - Tests randomized decision-making strategy
6. **Smart Strategy** (`smart_strategy.feature`) - Tests advanced AI strategy implementation

### Power Systems

1. **Abstract Power** (`abstract_power.feature`) - Tests the base power interface and mechanics
2. **Fascist Powers** (`fascist_powers.feature`) - Tests fascist executive actions like investigate loyalty, special election, and execution
3. **Communist Powers** (`communist_powers.feature`) - Tests communist powers including bugging, radicalization, five-year plan, and confession
4. **Article 48 Powers** (`article48_powers.feature`) - Tests presidential emergency powers (President Powers cards)
5. **Enabling Act Powers** (`enabling_act_powers.feature`) - Tests chancellor emergency powers (Chancellor Powers cards)
6. **Power Registry** (`power_registry.feature`) - Tests power registration and management system

### Game Components

1. **Policy Deck** (`policy_deck.feature`) - Tests policy deck creation, shuffling, and management
2. **Role Factory** (`role_factory.feature`) - Tests role assignment and creation based on player count and settings

## Test Organization

The BDD tests are organized in a clear hierarchy that mirrors the game's architecture:

### Directory Structure

```text
features/
├── *.feature               # Feature files describing game behavior
├── environment.py          # Test environment setup and configuration
└── steps/                  # Step definition implementations
    ├── *_steps.py          # Modular step definitions by feature area
    └── __pycache__/        # Python bytecode cache
```

### Feature File Categories

- **Core Features**: `game.feature`, `game_state.feature`, `board.feature`
- **Player Features**: `*_player.feature`, `player_factory.feature`
- **Strategy Features**: `*_strategy.feature`, `base_strategy.feature`
- **Power Features**: `*_powers.feature`, `abstract_power.feature`, `power_registry.feature`
- **Phase Features**: `*_phase.feature`
- **Component Features**: `policy_deck.feature`, `role_factory.feature`

### Step Definition Modules

Each step definition file corresponds to its related feature file and contains the implementation of Given/When/Then steps specific to that domain.

## Running the Tests

### Installation

First, install the required dependencies from the project requirements:

```bash
pip install -r requirements.txt
```

This will install behave along with all other project dependencies including:

- Core BDD framework: `behave`
- Testing utilities: `pytest`, `pytest-cov`
- Code quality tools: `black`, `pylint`, `isort`, `mypy`
- Type checking stubs for external libraries

### Locally

To run all tests:

```bash
python -m behave
```

To run a specific feature:

```bash
python -m behave features/game.feature
python -m behave features/election_phase.feature
python -m behave features/fascist_powers.feature
```

To run with verbose output:

```bash
behave --verbose
```

To run specific scenarios by name:

```bash
behave --name="player nomination"
```

To generate HTML reports:

```bash
pip install behave-html-formatter
behave -f behave_html_formatter:HTMLFormatter -o reports.html
```

### Coverage Analysis

To run BDD tests with code coverage analysis:

```bash
coverage run --source='.' --omit="*/features/*,*/steps/*" -m behave
coverage html
```

This will:

- Run all BDD tests while collecting coverage data
- Exclude the test files themselves (`features/` and `steps/` directories) from coverage analysis
- Generate an HTML coverage report in the `htmlcov/` directory

To view the coverage report:

- Open `htmlcov/index.html` in your web browser
- Review which parts of your source code are covered by the BDD tests
- Identify areas that may need additional test scenarios

You can also generate other coverage report formats:

```bash
# Generate console report
coverage report

# Generate XML report (useful for CI)
coverage xml
```

Note: Make sure you have the `coverage` package installed (it's included in `requirements.txt`).

### In GitHub Actions CI Pipeline

The BDD tests are automatically executed in the CI pipeline through GitHub Actions. The workflow is defined in `.github/workflows/bdd.yml` and runs on:

- **Push events** to `main`, `develop`, and `feat/**` branches
- **Pull requests** targeting `main`, `develop`, and `feat/**` branches

The CI pipeline:

1. Sets up Python 3.11 environment
2. Installs dependencies from `requirements.txt`
3. Runs all BDD tests using `behave`

To view test results:

- Check the **Actions** tab in your GitHub repository
- Click on the specific workflow run
- View the **BDD Test (Behave)** job results

## Known Issues and Limitations

- Some tests may require specific mock configurations or test data setup to run successfully
- Tests involving randomness (like strategy decisions or deck shuffling) may need deterministic mocking for consistent results
- Human player tests may require input simulation or mocking of console interactions
- Some complex game scenarios may be challenging to test due to the intricate state dependencies between game phases
- Power execution tests may require careful setup of game state preconditions
- Performance tests for large player counts may be limited by the BDD framework overhead

## Contributing

When adding new features to the Secret Hitler XL game, please follow these guidelines:

### Feature Files

1. **Create descriptive feature files** that clearly describe the expected behavior using Gherkin syntax
2. **Use consistent naming** - match feature file names with the corresponding source code modules
3. **Organize scenarios** by functional areas (game phases, player types, power systems, etc.)
4. **Include edge cases** and error scenarios alongside happy path tests

### Step Definitions

1. **Implement step definitions** in the `features/steps/` directory with descriptive file names
2. **Reuse existing steps** when possible to maintain consistency
3. **Use proper mocking** for complex dependencies and external interactions
4. **Maintain separation** between test logic and implementation details

### Testing Standards

1. **Ensure all existing tests pass** before submitting new features
2. **Test both positive and negative scenarios** for new functionality
3. **Validate error handling** and edge cases
4. **Check CI pipeline** passes for all targeted branches (`main`, `develop`, `feat/**`)

### Documentation

1. **Update this document** when adding new feature categories
2. **Document any new testing patterns** or conventions
3. **Include examples** of complex test scenarios for future reference

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Language Reference](https://cucumber.io/docs/gherkin/reference/)
