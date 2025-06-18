# Secret Hitler XL - Developer Guide

This document provides technical details about the Secret Hitler XL implementation for developers who want to understand or extend the codebase.

## Architecture Overview

The game follows a model-view-controller architecture, where:
- **Model**: Game state, board, players, policies, and roles
- **Controller**: Game logic, phases, and powers
- **View**: Currently only console-based, but designed to be extendable to other interfaces

---

## Key Components

### Game State

The game state is managed through the `EnhancedGameState` class, which tracks:
- Players and their status
- Election state
- Policy tracks
- Presidential powers
- Game phase

### Game Board

The game board is represented by the `GameBoard` class, which handles:
- Policy trackers (Liberal, Fascist, Communist)
- Policy deck management
- Presidential powers associated with each track position

### Players

Players are represented by the `EnhancedPlayer` abstract class and implemented as:
- `AIPlayer`: Computer-controlled player using various strategies

### Strategies

AI strategies are implemented using the Strategy pattern:
- `RandomStrategy`: Makes random decisions
- `LiberalStrategy`: Prioritizes liberal policies and trusted players
- `FascistStrategy`: Prioritizes fascist policies and deception
- `CommunistStrategy`: Prioritizes communist policies and balance
- `SmartStrategy`: Prioritizes choices that benefit their party and bots have memory and suspicions of other players.

### Policies

Policies are implemented as classes derived from the base `Policy` class:
- `Liberal`: Liberal policies
- `Fascist`: Fascist policies
- `Communist`: Communist policies
- `AntiPolicy`: Anti-policies (Anti-Liberal, Anti-Fascist, Anti-Communist)
- `EmergencyPower`: Emergency powers (Article 48, Enabling Act)

### Presidential Powers

Presidential powers are implemented using the Command pattern:
- `InvestigateLoyalty`: Investigate a player's party membership
- `SpecialElection`: Choose the next president
- `PolicyPeek`: Look at the top 3 policies
- `Execution`: Kill a player
- `Confession`: Force a player to reveal their party membership
- `Bugging`: See the next policies that will be drawn
- `FiveYearPlan`: Draw 5 policies and enact one
- `Congress`: Block or enable presidential powers
- `Radicalization`: Convert a player to communist

### Game Phases

Game phases are implemented using the State pattern:
- `SetupPhase`: Initialize the game
- `OpeningPhase`: Start the game and reveal roles
- `ElectionPhase`: Elect a government
- `LegislativePhase`: Enact policies
- `ExecutiveActionPhase`: Use presidential powers
- `EndPhase`: End the game and determine winner

---

## Design Patterns Implementation

The Secret Hitler XL codebase implements several core design patterns to ensure maintainability, extensibility, and clear separation of concerns. Below are the main patterns used, with real code examples and explanations.

### 1. Factory Pattern

**Purpose:** Centralizes and encapsulates object creation logic for policies, players, and roles.

#### PolicyFactory Example (`src/policies/policy_factory.py`):
```python
class PolicyFactory:
    @staticmethod
    def create_policy_deck(player_count, with_communists, with_anti_policies, with_emergency_powers):
        policies = []
        # ... logic to add policies ...
        if with_anti_policies:
            for i, policy in enumerate(policies):
                if policy.type == "fascist":
                    policies[i] = AntiCommunist()
                    break
        return policies
```

#### PlayerFactory Example (`src/players/player_factory.py`):
```python
class PlayerFactory:
    @staticmethod
    def create_player(player_id, name, role, state, strategy_type):
        if strategy_type == "ai":
            return AIPlayer(player_id, name, role, state, strategy_type)
        else:
            return HumanPlayer(player_id, name, role, state)
```

#### RoleFactory Example (`src/roles/role_factory.py`):
```python
class RoleFactory:
    @staticmethod
    def create_roles(player_count, with_communists):
        roles = []
        # ... logic to assign roles ...
        return roles
```

**Benefits:**
- Decouples object creation from business logic
- Makes it easy to add new types of policies, players, or roles
- Supports dynamic game configuration

---

### 2. Strategy Pattern

**Purpose:** Encapsulates different algorithms/behaviors for AI players, allowing them to be swapped at runtime.

#### Base Strategy Example (`src/players/strategies/base_strategy.py`):
```python
class BaseStrategy(ABC):
    @abstractmethod
    def nominate_chancellor(self, eligible_players):
        pass
    @abstractmethod
    def vote(self, president, chancellor):
        pass
    # ... other abstract methods ...
```

#### Concrete Strategy Example:
```python
class LiberalStrategy(BaseStrategy):
    def nominate_chancellor(self, eligible_players):
        # Prefer trusted liberal players
        ...
    def vote(self, president, chancellor):
        # Vote yes if both are trusted
        ...
```

#### Strategy Assignment Example:
```python
def apply_strategy_to_player(self, player, strategy_type="smart"):
    if strategy_type == "random":
        player.strategy = RandomStrategy(player)
    elif strategy_type == "role":
        if player.is_fascist or player.is_hitler:
            player.strategy = FascistStrategy(player)
        elif player.is_communist:
            player.strategy = CommunistStrategy(player)
        else:
            player.strategy = LiberalStrategy(player)
    else:
        player.strategy = SmartStrategy(player)
```
**Benefits:**
- Modular and extensible AI
- Easy to add new strategies or change behavior at runtime
- Each strategy can be tested independently

---

### 3. State Pattern

**Purpose:** Models the game as a set of phases (states), each with its own logic and transitions.

#### Abstract Phase Example (`src/game/phases/abstract_phase.py`):
```python
class GamePhase(ABC):
    def __init__(self, game):
        self.game = game
    @abstractmethod
    def execute(self):
        pass
```

#### Concrete Phase Example:
```python
class ElectionPhase(GamePhase):
    def execute(self):
        # Election logic here
        # Return next phase
        ...
```

**Benefits:**
- Clean separation of phase logic
- Easy to add or modify phases
- Each phase knows how to transition to the next

---

### 4. Command Pattern

**Purpose:** Encapsulates presidential powers as command objects that can be executed.

#### Abstract Power Example (`src/game/powers/abstract_power.py`):
```python
class Power(ABC):
    def __init__(self, game):
        self.game = game
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
```

#### Concrete Power Example:
```python
class InvestigateLoyalty(Power):
    def execute(self, target_player):
        # Reveal party membership
        ...
```

**Benefits:**
- Each power is self-contained
- Easy to add new powers
- Powers can be queued, logged, or extended

---

## Extending the Game

- **Extending the Game:**
  - To add new roles, policies, powers, or strategies, create a new class and register it in the appropriate factory or registry.
  - Update the relevant phase or game logic to use the new component.
- **Testing:**
  - Each pattern allows for isolated unit testing of strategies, powers, and phases.
- **Configuration:**
  - Game setup is highly configurable via factories and state objects.
- **Logging:**
  - The `GameLogger` class provides centralized logging for debugging and analytics.
- **AI Flexibility:**
  - Strategies can be swapped at runtime (e.g., Oktoberfest event).
- **Phase Transitions:**
  - The main game loop transitions between phases using the State pattern, making the flow easy to follow and extend.

For more details, see the code in the `src/` directory and the UML diagrams for class and sequence structure.

### Adding New Roles

To add a new role:
1. Add a new role class in `src/roles/role.py`
2. Update the `RoleFactory` to create the new role
3. Update role assignment in `SHXLGame.assign_players()`

### Adding New Policies

To add a new policy type:
1. Add a new policy class in `src/policies/policy.py`
2. Update the `PolicyFactory` to create the new policy
3. Update policy deck initialization in `GameBoard.initialize_policy_deck()`
4. Implement the policy effects in `GameBoard.enact_policy()`

### Adding New Powers

To add a new presidential power:
1. Add a new power class in `src/game/presidential_powers.py`
2. Register the power in `PowerRegistry`
3. Update the power slot assignments in `GameBoard._setup_fascist_powers()` or `GameBoard._setup_communist_powers()`

### Adding New AI Strategies

To add a new AI strategy:
1. Add a new strategy class in `src/players/ai_strategies.py`
2. Update the `PlayerFactory` to use the new strategy
