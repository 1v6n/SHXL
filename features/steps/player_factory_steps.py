from unittest.mock import MagicMock, Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.players.ai_player import AIPlayer
from src.players.human_player import HumanPlayer
from src.players.player_factory import PlayerFactory
from src.players.strategies import (
    CommunistStrategy,
    FascistStrategy,
    LiberalStrategy,
    RandomStrategy,
    SmartStrategy,
)
from src.roles.role import Role


class MockGameState:
    """Mock game state for testing PlayerFactory"""

    def __init__(self):
        self.players = []
        self.ai_strategy_type = None


class MockRole:
    """Mock role for testing"""

    def __init__(self, role_type):
        # Handle both English and Spanish role names
        role_mapping = {
            "liberal": "liberal",
            "fascist": "fascist",
            "fascista": "fascist",  # Spanish
            "communist": "communist",
            "comunista": "communist",  # Spanish
            "hitler": "hitler",
        }

        self.role = role_mapping.get(role_type.lower(), role_type)

        # Set party_membership to match real Role classes
        if self.role == "liberal":
            self.party_membership = "liberal"
        elif self.role == "fascist":
            self.party_membership = "fascist"
        elif self.role == "communist":
            self.party_membership = "communist"
        elif self.role == "hitler":
            self.party_membership = "fascist"  # Hitler has fascist party membership
        else:
            self.party_membership = ""

    @property
    def is_liberal(self):
        return self.role == "liberal"

    @property
    def is_fascist(self):
        return self.role == "fascist"

    @property
    def is_communist(self):
        return self.role == "communist"

    @property
    def is_hitler(self):
        return self.role == "hitler"

    def __repr__(self):
        return self.role.title()


def create_mock_player_with_role(
    player_id, name, role_type, state, player_class=AIPlayer
):
    """Helper to create a mock player with a specific role"""
    role = MockRole(role_type) if role_type else None
    player = player_class(player_id, name, role, state)

    # Set role properties for AI players
    if hasattr(player, "role") and role:
        player.role = role
        # Note: Don't set convenience properties as they are computed from role

    return player


# Background steps
@given("un estado de juego mock para factory")
def step_impl_mock_game_state_for_factory(context):
    context.mock_state = MockGameState()
    context.factory = PlayerFactory()


# When steps - Player creation
@when(
    'creo un jugador AI con ID {player_id:d}, nombre "{name}", sin rol, y estrategia "{strategy_type}"'
)
def step_impl_create_ai_player(context, player_id, name, strategy_type):
    context.player = PlayerFactory.create_player(
        player_id, name, None, context.mock_state, strategy_type, "ai"
    )


@when('creo un jugador humano con ID {player_id:d}, nombre "{name}", sin rol')
def step_impl_create_human_player(context, player_id, name):
    context.player = PlayerFactory.create_player(
        player_id, name, None, context.mock_state, "smart", "human"
    )


# Given steps - Player setup
@given("un jugador AI {role_type} sin estrategia asignada")
def step_impl_ai_player_without_strategy(context, role_type):
    context.player = create_mock_player_with_role(
        1, "TestPlayer", role_type, context.mock_state
    )
    # Set strategy to None to indicate it's not assigned yet
    # but keep the attribute so apply_strategy_to_player works
    context.player.strategy = None


@given("un jugador humano sin atributo strategy")
def step_impl_human_player_without_strategy(context):
    context.player = HumanPlayer(1, "TestHuman", None, context.mock_state)


@given("una lista de {count:d} jugadores AI con roles {role_list}")
def step_impl_list_of_ai_players_with_roles(context, count, role_list):
    # Parse role list like "[liberal, fascist, communist]"
    roles = role_list.strip("[]").split(", ")
    context.players = []
    for i, role in enumerate(roles):
        player = create_mock_player_with_role(
            i, f"Player{i}", role.strip(), context.mock_state
        )
        context.players.append(player)


@given("una lista mixta de {count:d} jugadores {player_list}")
def step_impl_mixed_list_of_players(context, count, player_list):
    # Parse player list like "[AI liberal, humano, AI fascista, AI comunista]"
    player_specs = player_list.strip("[]").split(", ")
    context.players = []

    for i, spec in enumerate(player_specs):
        spec = spec.strip()
        player = None  # Initialize player variable
        if spec.startswith("AI "):
            role = spec.replace("AI ", "")
            player = create_mock_player_with_role(
                i, f"AIPlayer{i}", role, context.mock_state, AIPlayer
            )
        elif spec == "humano":
            player = HumanPlayer(i, f"HumanPlayer{i}", None, context.mock_state)

        if player is not None:  # Only append if player was created
            context.players.append(player)


# When steps - Strategy application
@when('aplico estrategia "{strategy_type}" al jugador')
def step_impl_apply_strategy_to_player(context, strategy_type):
    context.factory.apply_strategy_to_player(context.player, strategy_type)


@when(
    'creo {count:d} jugadores con estrategia "{strategy_type}" y sin jugadores humanos'
)
def step_impl_create_multiple_players_no_humans(context, count, strategy_type):
    context.created_players = context.factory.create_players(
        count, context.mock_state, strategy_type
    )


@when(
    'creo {count:d} jugadores con estrategia "{strategy_type}" y jugadores humanos en posiciones {positions}'
)
def step_impl_create_multiple_players_with_humans(
    context, count, strategy_type, positions
):
    # Parse positions like "[1, 3]"
    human_indices = []
    if positions != "None":
        indices_str = positions.strip("[]").split(", ")
        human_indices = [int(idx.strip()) for idx in indices_str if idx.strip()]

    context.created_players = context.factory.create_players(
        count, context.mock_state, strategy_type, human_indices
    )


@when(
    'creo {count:d} jugadores con estrategia "{strategy_type}" y jugadores humanos None'
)
def step_impl_create_multiple_players_none_humans(context, count, strategy_type):
    context.created_players = context.factory.create_players(
        count, context.mock_state, strategy_type, None
    )


@when('actualizo las estrategias de todos los jugadores con tipo "{strategy_type}"')
def step_impl_update_all_strategies(context, strategy_type):
    context.factory.update_player_strategies(context.players, strategy_type)


# Then steps - Player type verification
@then("el jugador debe ser una instancia de AIPlayer")
def step_impl_player_is_ai(context):
    assert isinstance(
        context.player, AIPlayer
    ), f"Expected AIPlayer, got {type(context.player)}"


@then("el jugador debe ser una instancia de HumanPlayer")
def step_impl_player_is_human(context):
    assert isinstance(
        context.player, HumanPlayer
    ), f"Expected HumanPlayer, got {type(context.player)}"


@then("el jugador debe tener ID {expected_id:d}")
def step_impl_player_has_id(context, expected_id):
    assert (
        context.player.id == expected_id
    ), f"Expected ID {expected_id}, got {context.player.id}"


@then("el jugador debe tener rol None")
def step_impl_player_has_none_role(context):
    assert context.player.role is None, f"Expected None role, got {context.player.role}"


@then("el jugador no debe tener atributo strategy")
def step_impl_player_has_no_strategy(context):
    assert not hasattr(
        context.player, "strategy"
    ), "Player should not have strategy attribute"


# Then steps - Strategy verification
@then("el jugador debe usar estrategia RandomStrategy")
def step_impl_player_uses_random_strategy(context):
    assert isinstance(
        context.player.strategy, RandomStrategy
    ), f"Expected RandomStrategy, got {type(context.player.strategy)}"


@then("el jugador debe usar estrategia LiberalStrategy")
def step_impl_player_uses_liberal_strategy(context):
    assert isinstance(
        context.player.strategy, LiberalStrategy
    ), f"Expected LiberalStrategy, got {type(context.player.strategy)}"


@then("el jugador debe usar estrategia FascistStrategy")
def step_impl_player_uses_fascist_strategy(context):
    assert isinstance(
        context.player.strategy, FascistStrategy
    ), f"Expected FascistStrategy, got {type(context.player.strategy)}"


@then("el jugador debe usar estrategia CommunistStrategy")
def step_impl_player_uses_communist_strategy(context):
    assert isinstance(
        context.player.strategy, CommunistStrategy
    ), f"Expected CommunistStrategy, got {type(context.player.strategy)}"


@then("el jugador debe usar estrategia SmartStrategy")
def step_impl_player_uses_smart_strategy(context):
    assert isinstance(
        context.player.strategy, SmartStrategy
    ), f"Expected SmartStrategy, got {type(context.player.strategy)}"


# Then steps - Multiple players verification
@then("debo tener {count:d} jugadores en total")
def step_impl_total_player_count(context, count):
    assert (
        len(context.created_players) == count
    ), f"Expected {count} players, got {len(context.created_players)}"


@then("todos los jugadores deben ser instancias de AIPlayer")
def step_impl_all_players_are_ai(context):
    for i, player in enumerate(context.created_players):
        assert isinstance(
            player, AIPlayer
        ), f"Player at index {i} is not AIPlayer: {type(player)}"


@then('los nombres deben seguir el patrón "Bot {{index}}"')
def step_impl_names_follow_bot_pattern(context):
    for i, player in enumerate(context.created_players):
        expected_name = f"Bot {i}"
        assert (
            player.name == expected_name
        ), f"Expected name '{expected_name}', got '{player.name}'"


@then('todos los nombres deben seguir el patrón "Bot {{index}}"')
def step_impl_all_names_follow_bot_pattern(context):
    step_impl_names_follow_bot_pattern(context)


@then('el estado debe almacenar la estrategia "{strategy_type}"')
def step_impl_state_stores_strategy(context, strategy_type):
    assert (
        context.mock_state.ai_strategy_type == strategy_type
    ), f"Expected strategy '{strategy_type}', got '{context.mock_state.ai_strategy_type}'"


@then(
    'el jugador en posición {position:d} debe ser AIPlayer con nombre "{expected_name}"'
)
def step_impl_player_at_position_is_ai_with_name(context, position, expected_name):
    player = context.created_players[position]
    assert isinstance(
        player, AIPlayer
    ), f"Player at position {position} is not AIPlayer: {type(player)}"
    assert (
        player.name == expected_name
    ), f"Expected name '{expected_name}', got '{player.name}'"


@then(
    'el jugador en posición {position:d} debe ser HumanPlayer con nombre "{expected_name}"'
)
def step_impl_player_at_position_is_human_with_name(context, position, expected_name):
    player = context.created_players[position]
    assert isinstance(
        player, HumanPlayer
    ), f"Player at position {position} is not HumanPlayer: {type(player)}"
    assert (
        player.name == expected_name
    ), f"Expected name '{expected_name}', got '{player.name}'"


# Then steps - Strategy updates verification
@then("el jugador liberal debe usar estrategia LiberalStrategy")
def step_impl_liberal_player_uses_liberal_strategy(context):
    liberal_player = next(
        p for p in context.players if hasattr(p, "is_liberal") and p.is_liberal
    )
    assert isinstance(
        liberal_player.strategy, LiberalStrategy
    ), f"Liberal player should use LiberalStrategy, got {type(liberal_player.strategy)}"


@then("el jugador fascista debe usar estrategia FascistStrategy")
def step_impl_fascist_player_uses_fascist_strategy(context):
    fascist_player = next(
        p for p in context.players if hasattr(p, "is_fascist") and p.is_fascist
    )
    assert isinstance(
        fascist_player.strategy, FascistStrategy
    ), f"Fascist player should use FascistStrategy, got {type(fascist_player.strategy)}"


@then("el jugador comunista debe usar estrategia CommunistStrategy")
def step_impl_communist_player_uses_communist_strategy(context):
    communist_player = next(
        p for p in context.players if hasattr(p, "is_communist") and p.is_communist
    )
    assert isinstance(
        communist_player.strategy, CommunistStrategy
    ), f"Communist player should use CommunistStrategy, got {type(communist_player.strategy)}"


@then("el jugador AI liberal debe usar estrategia SmartStrategy")
def step_impl_ai_liberal_uses_smart_strategy(context):
    ai_liberal = next(
        p
        for p in context.players
        if isinstance(p, AIPlayer) and hasattr(p, "is_liberal") and p.is_liberal
    )
    assert isinstance(
        ai_liberal.strategy, SmartStrategy
    ), f"AI Liberal should use SmartStrategy, got {type(ai_liberal.strategy)}"


@then("el jugador humano no debe tener cambios en strategy")
def step_impl_human_player_no_strategy_changes(context):
    human_player = next(p for p in context.players if isinstance(p, HumanPlayer))
    assert not hasattr(
        human_player, "strategy"
    ), "Human player should not have strategy attribute"


@then("el jugador AI fascista debe usar estrategia SmartStrategy")
def step_impl_ai_fascist_uses_smart_strategy(context):
    ai_fascist = next(
        p
        for p in context.players
        if isinstance(p, AIPlayer) and hasattr(p, "is_fascist") and p.is_fascist
    )
    assert isinstance(
        ai_fascist.strategy, SmartStrategy
    ), f"AI Fascist should use SmartStrategy, got {type(ai_fascist.strategy)}"


@then("el jugador AI comunista debe usar estrategia SmartStrategy")
def step_impl_ai_communist_uses_smart_strategy(context):
    ai_communist = next(
        p
        for p in context.players
        if isinstance(p, AIPlayer) and hasattr(p, "is_communist") and p.is_communist
    )
    assert isinstance(
        ai_communist.strategy, SmartStrategy
    ), f"AI Communist should use SmartStrategy, got {type(ai_communist.strategy)}"
