"""Step definitions for Communist Strategy behavior tests.

This module contains all the step definitions used in Behave tests for the
CommunistStrategy class. It provides setup, action, and verification steps
for testing communist player decision-making in Secret Hitler XL.

Example:
    Run the communist strategy tests with:
        behave features/comunist_strategy.feature

Note:
    These step definitions use Mock objects to simulate game state and other
    players, allowing for isolated testing of the communist strategy logic.
"""

from random import choice
from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.players.strategies.base_strategy import PlayerStrategy
from src.players.strategies.communist_strategy import CommunistStrategy


def ensure_mock_player_setup_communist(context):
    """Ensure mock player is properly set up for communist strategy tests.

    Sets up a complete mock player with all necessary attributes for testing
    communist strategy behavior. Includes game state, tracks, known players,
    and role information.

    Args:
        context: Behave context object containing test state.

    Note:
        This function is idempotent - it can be called multiple times safely.
        It creates real dictionaries for known_communists and known_affiliations
        to avoid Mock object issues in tests.
    """
    if not hasattr(context, "mock_player"):
        context.mock_player = Mock()

    context.mock_player.name = "Communist Player"
    context.mock_player.id = 1

    # Always ensure inspected_players is a real dictionary, not a Mock
    if not hasattr(context.mock_player, "inspected_players") or not isinstance(
        context.mock_player.inspected_players, dict
    ):
        context.mock_player.inspected_players = {}

    # Ensure state exists with all necessary attributes
    if not hasattr(context.mock_player, "state") or context.mock_player.state is None:
        context.mock_player.state = Mock()

    # Board with tracks - CommunistStrategy expects state.board tracks
    context.mock_player.state.board = Mock()
    context.mock_player.state.board.communist_track = 0
    context.mock_player.state.board.liberal_track = 0
    context.mock_player.state.board.fascist_track = 0

    # Track size attributes as integers (not Mocks)
    context.mock_player.state.board.communist_track_size = 5
    context.mock_player.state.board.liberal_track_size = 5
    context.mock_player.state.board.fascist_track_size = 6

    # Also set direct tracks for compatibility
    context.mock_player.state.communist_track = 0
    context.mock_player.state.liberal_track = 0
    context.mock_player.state.fascist_track = 0

    # Direct track size attributes as integers (not Mocks)
    context.mock_player.state.communist_track_size = 5
    context.mock_player.state.liberal_track_size = 5
    context.mock_player.state.fascist_track_size = 6

    context.mock_player.state.round_number = 1
    context.mock_player.state.election_tracker = 0
    context.mock_player.state.marked_for_execution = None
    context.mock_player.state.last_discarded = None

    # Communist-specific attributes
    context.mock_player.known_communists = []
    context.mock_player.known_affiliations = {}

    # Role attributes - communist by default
    context.mock_player.is_liberal = False
    context.mock_player.is_fascist = False
    context.mock_player.is_communist = True
    context.mock_player.is_hitler = False

    context.result = None  # Initialize result to None for clarity in steps


# Given steps (Setup)

@given("un jugador comunista mock")
def step_impl_communist_mock_player(context):
    """Create a mock communist player.

    Args:
        context: Behave context object.
    """
    context.mock_player = Mock()
    ensure_mock_player_setup_communist(context)


@given("una estrategia comunista")
@given("una estrategia comunista con el jugador")
@given("creo una estrategia comunista con el jugador")
def step_impl_communist_strategy(context):
    """Create a communist strategy instance.

    Args:
        context: Behave context object.
    """
    ensure_mock_player_setup_communist(context)
    context.strategy = CommunistStrategy(context.mock_player)


@given("una lista de {count:d} jugadores elegibles para canciller (comunista)")
def step_impl_eligible_players_chancellor(context, count):
    """Create eligible players for chancellor nomination.

    Args:
        context: Behave context object.
        count (int): Number of eligible players to create.
    """
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        player.is_communist = False
        player.is_fascist = False
        player.is_liberal = True  # Default to liberal
        player.is_hitler = False
        context.eligible_players.append(player)


@given("una lista de {count:d} jugadores elegibles para ejecución (comunista)")
def step_impl_eligible_players_execution(context, count):
    """Create eligible players for execution.

    Args:
        context: Behave context object.
        count (int): Number of eligible players to create.
    """
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        player.is_communist = False
        player.is_fascist = False
        player.is_liberal = True  # Default to liberal
        player.is_hitler = False
        context.eligible_players.append(player)


@given("una lista de {count:d} jugadores elegibles para radicalización (comunista)")
def step_impl_eligible_players_radicalization(context, count):
    """Create eligible players for radicalization.

    Args:
        context: Behave context object.
        count (int): Number of eligible players to create.
    """
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        player.is_communist = False
        player.is_fascist = False
        player.is_liberal = True  # Default to liberal
        player.is_hitler = False
        context.eligible_players.append(player)


@given("una lista de {count:d} jugadores elegibles para marcado (comunista)")
def step_impl_eligible_players_marking(context, count):
    """Create eligible players for marking.

    Args:
        context: Behave context object.
        count (int): Number of eligible players to create.
    """
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        player.is_communist = False
        player.is_fascist = False
        player.is_liberal = True  # Default to liberal
        player.is_hitler = False
        context.eligible_players.append(player)


@given("una lista de {count:d} jugadores elegibles para espionaje (comunista)")
def step_impl_eligible_players_spy(context, count):
    """Create eligible players for spying.

    Args:
        context: Behave context object.
        count (int): Number of eligible players to create.
    """
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        player.is_communist = False
        player.is_fascist = False
        player.is_liberal = True  # Default to liberal
        player.is_hitler = False
        context.eligible_players.append(player)


@given("una lista de {count:d} jugadores elegibles para revelación (comunista)")
def step_impl_eligible_players_reveal(context, count):
    """Create eligible players for revelation.

    Args:
        context: Behave context object.
        count (int): Number of eligible players to create.
    """
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        player.is_communist = False
        player.is_fascist = False
        player.is_liberal = True  # Default to liberal
        player.is_hitler = False
        context.eligible_players.append(player)


@given("el jugador {player_id:d} es comunista")
def step_impl_player_is_communist(context, player_id):
    """Set player as communist.

    Marks a player as communist both in the eligible players list and in the
    mock player's known_communists list for proper testing.

    Args:
        context: Behave context object.
        player_id (int): ID of the player to mark as communist.
    """
    ensure_mock_player_setup_communist(context)

    # Add to known communists
    if player_id not in context.mock_player.known_communists:
        context.mock_player.known_communists.append(player_id)

    # Set in eligible players if they exist
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                player.is_communist = True
                player.is_fascist = False
                player.is_liberal = False
                player.is_hitler = False
                break


@given("ningún jugador es comunista")
def step_impl_no_communist_players(context):
    """Ensure no players are communist.

    Args:
        context: Behave context object.
    """
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            player.is_communist = False


@given("el jugador {player_id:d} es liberal")
def step_impl_player_is_liberal(context, player_id):
    """Set player as liberal.

    Args:
        context: Behave context object.
        player_id (int): ID of the player to mark as liberal.
    """
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                player.is_liberal = True
                player.is_fascist = False
                player.is_communist = False
                player.is_hitler = False
                break


@given("el jugador {player_id:d} es fascista")
def step_impl_player_is_fascist(context, player_id):
    """Set player as fascist.

    Args:
        context: Behave context object.
        player_id (int): ID of the player to mark as fascist.
    """
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                player.is_fascist = True
                player.is_liberal = False
                player.is_communist = False
                player.is_hitler = False
                break


@given("el jugador {player_id:d} es conocido como fascista")
def step_impl_known_fascist(context, player_id):
    """Mark player as known fascist.

    Sets the player as a known fascist in both inspected_players and
    known_affiliations for consistency across different strategy methods.

    Args:
        context: Behave context object.
        player_id (int): ID of the player to mark as known fascist.
    """
    ensure_mock_player_setup_communist(context)
    # Set in both structures for consistency
    context.mock_player.inspected_players[player_id] = "fascist"
    context.mock_player.known_affiliations[player_id] = "fascist"

    # Also set in eligible players if they exist
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                player.is_fascist = True
                player.is_liberal = False
                player.is_communist = False
                player.is_hitler = False
                break


@given("el jugador {player_id:d} es conocido como liberal")
def step_impl_known_liberal(context, player_id):
    """Mark player as known liberal.

    Sets the player as a known liberal in both inspected_players and
    known_affiliations for consistency across different strategy methods.

    Args:
        context: Behave context object.
        player_id (int): ID of the player to mark as known liberal.
    """
    ensure_mock_player_setup_communist(context)
    # Set in both structures for consistency
    context.mock_player.inspected_players[player_id] = "liberal"
    context.mock_player.known_affiliations[player_id] = "liberal"

    # Also set in eligible players if they exist
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                player.is_liberal = True
                player.is_fascist = False
                player.is_communist = False
                player.is_hitler = False
                break


@given("el jugador {player_id:d} no fue inspeccionado")
def step_impl_player_not_inspected(context, player_id):
    """Mark player as not inspected.

    Removes the player from the inspected_players dictionary if present.

    Args:
        context: Behave context object.
        player_id (int): ID of the player to mark as not inspected.
    """
    ensure_mock_player_setup_communist(context)
    if player_id in context.mock_player.inspected_players:
        del context.mock_player.inspected_players[player_id]


@given("una lista de {count:d} políticas: {policy_list}")
def step_impl_policies_list(context, count, policy_list):
    """Create list of policies.

    Args:
        context: Behave context object.
        count (int): Expected number of policies (for validation).
        policy_list (str): Comma-separated list of policy types.
    """
    policy_names = [p.strip().strip('"') for p in policy_list.split(",")]
    context.policies = []
    for policy_name in policy_names:
        policy = Mock()
        policy.type = policy_name
        context.policies.append(policy)


@given("una lista de políticas para veto comunista: {policy_list}")
def step_impl_policies_for_veto_communist(context, policy_list):
    """Create list of policies for veto decision.

    Args:
        context: Behave context object.
        policy_list (str): Comma-separated list of policy types.
    """
    policy_names = [p.strip().strip('"') for p in policy_list.split(",")]
    context.policies = []
    for policy_name in policy_names:
        policy = Mock()
        policy.type = policy_name
        context.policies.append(policy)


@given("un presidente comunista")
def step_impl_communist_president(context):
    """Create communist president.

    Creates a mock communist president and adds them to the known_communists
    list so the strategy recognizes them as an ally.

    Args:
        context: Behave context object.
    """
    ensure_mock_player_setup_communist(context)

    player = Mock()
    player.id = 1
    player.name = "Communist President"
    player.is_communist = True
    player.is_fascist = False
    player.is_liberal = False
    player.is_hitler = False

    # Make the president known as communist
    context.mock_player.known_communists.append(player.id)

    context.president = player


@given("un canciller comunista")
def step_impl_communist_chancellor(context):
    """Create communist chancellor.

    Creates a mock communist chancellor and adds them to the known_communists
    list so the strategy recognizes them as an ally.

    Args:
        context: Behave context object.
    """
    ensure_mock_player_setup_communist(context)

    player = Mock()
    player.id = 2
    player.name = "Communist Chancellor"
    player.is_communist = True
    player.is_fascist = False
    player.is_liberal = False
    player.is_hitler = False

    # Make the chancellor known as communist
    context.mock_player.known_communists.append(player.id)

    context.chancellor = player


@given("un presidente fascista")
def step_impl_fascist_president(context):
    """Create fascist president.

    Args:
        context: Behave context object.
    """
    player = Mock()
    player.id = 97
    player.name = "Fascist President"
    player.is_fascist = True
    player.is_communist = False
    player.is_liberal = False
    player.is_hitler = False
    context.president = player


@given("un canciller fascista")
def step_impl_fascist_chancellor(context):
    """Create fascist chancellor.

    Args:
        context: Behave context object.
    """
    player = Mock()
    player.id = 96
    player.name = "Fascist Chancellor"
    player.is_fascist = True
    player.is_communist = False
    player.is_liberal = False
    player.is_hitler = False
    context.chancellor = player


@given("una política {policy_type} para propaganda comunista")
def step_impl_propaganda_policy(context, policy_type):
    """Create policy for propaganda decision.

    Args:
        context: Behave context object.
        policy_type (str): Type of policy (communist, liberal, fascist).
    """
    policy = Mock()
    policy.type = policy_type
    context.policy = policy


@given("un comunista está marcado para ejecución")
def step_impl_communist_marked_execution(context):
    """Create communist marked for execution.

    Args:
        context: Behave context object.
    """
    ensure_mock_player_setup_communist(context)

    marked_player = Mock()
    marked_player.id = 95
    marked_player.name = "Marked Communist"
    marked_player.is_communist = True
    marked_player.is_fascist = False
    marked_player.is_liberal = False
    marked_player.is_hitler = False

    context.mock_player.state.marked_for_execution = marked_player


@given("un fascista está marcado para ejecución")
def step_impl_fascist_marked_execution(context):
    """Create fascist marked for execution.

    Creates a fascist player marked for execution and adds them to the
    known_affiliations so the strategy recognizes them as an enemy.

    Args:
        context: Behave context object.
    """
    ensure_mock_player_setup_communist(context)

    marked_player = Mock()
    marked_player.id = 94
    marked_player.name = "Marked Fascist"
    marked_player.is_fascist = True
    marked_player.is_communist = False
    marked_player.is_liberal = False
    marked_player.is_hitler = False

    # Make the fascist known to the communist strategy
    context.mock_player.known_affiliations[94] = "fascist"

    context.mock_player.state.marked_for_execution = marked_player


@given("políticas sin comunistas para propuesta de veto")
def step_impl_no_communist_veto_policies(context):
    """Create policies without communists for veto proposal.

    Args:
        context: Behave context object.
    """
    context.policies = []

    policy1 = Mock()
    policy1.type = "liberal"
    context.policies.append(policy1)

    policy2 = Mock()
    policy2.type = "fascist"
    context.policies.append(policy2)


@given("una política {policy_type} como última descartada (comunista)")
def step_impl_last_discarded_policy(context, policy_type):
    """Set last discarded policy.

    Args:
        context: Behave context object.
        policy_type (str): Type of the last discarded policy.
    """
    ensure_mock_player_setup_communist(context)

    policy = Mock()
    policy.type = policy_type
    context.mock_player.state.last_discarded = policy


@given("el estado tiene políticas fascistas y liberales")
def step_impl_state_has_fascist_liberal_policies(context):
    """Set state with fascist and liberal policies on tracks.

    Args:
        context: Behave context object.
    """
    ensure_mock_player_setup_communist(context)
    context.mock_player.state.board.fascist_track = 2
    context.mock_player.state.board.liberal_track = 1
    context.mock_player.state.fascist_track = 2
    context.mock_player.state.liberal_track = 1


# When steps (Actions)

@when("creo una estrategia comunista con el jugador")
def step_impl_create_communist_strategy(context):
    """Create communist strategy with player.

    Args:
        context: Behave context object.
    """
    ensure_mock_player_setup_communist(context)
    context.strategy = CommunistStrategy(context.mock_player)


@when("la estrategia comunista nomina un canciller")
def step_impl_communist_nominate_chancellor(context):
    """Communist strategy nominates chancellor.

    Args:
        context: Behave context object.
    """
    context.result = context.strategy.nominate_chancellor(context.eligible_players)


@when("la estrategia comunista filtra las políticas")
def step_impl_communist_filter_policies(context):
    """Communist strategy filters policies.

    Args:
        context: Behave context object.
    """
    result = context.strategy.filter_policies(context.policies)
    context.result = result
    # For compatibility with discard steps that expect context.discarded
    if len(result) == 2:  # (kept_policies, discarded_policy)
        context.kept_policies, context.discarded = result
    else:
        context.kept_policies = result
        context.discarded = None


@when("la estrategia comunista elige una política")
def step_impl_communist_choose_policy(context):
    """Communist strategy chooses policy.

    Args:
        context: Behave context object.
    """
    result = context.strategy.choose_policy(context.policies)
    context.chosen, context.discarded = result
    context.result = result


@when("la estrategia comunista vota en el gobierno")
def step_impl_communist_vote(context):
    """Communist strategy votes on government.

    Args:
        context: Behave context object.
    """
    context.vote_result = context.strategy.vote(context.president, context.chancellor)
    context.result = context.vote_result


@when("la estrategia comunista decide sobre veto")
def step_impl_communist_veto(context):
    """Communist strategy decides on veto.

    Args:
        context: Behave context object.
    """
    context.veto_result = context.strategy.veto(context.policies)
    context.result = context.veto_result


@when("la estrategia comunista elige un jugador para ejecutar")
def step_impl_communist_choose_execute(context):
    """Communist strategy chooses player to execute.

    Args:
        context: Behave context object.
    """
    context.result = context.strategy.choose_player_to_kill(context.eligible_players)


@when("la estrategia comunista elige un jugador para radicalizar")
def step_impl_communist_choose_radicalize(context):
    """Communist strategy chooses player to radicalize.

    Args:
        context: Behave context object.
    """
    context.result = context.strategy.choose_player_to_radicalize(context.eligible_players)


@when("la estrategia comunista elige un jugador para marcar")
def step_impl_communist_choose_mark(context):
    """Communist strategy chooses player to mark.

    Args:
        context: Behave context object.
    """
    context.result = context.strategy.choose_player_to_mark(context.eligible_players)


@when("la estrategia comunista elige un jugador para espionar")
def step_impl_communist_choose_spy(context):
    """Communist strategy chooses player to spy on.

    Args:
        context: Behave context object.
    """
    context.result = context.strategy.choose_player_to_inspect(context.eligible_players)

@when("la estrategia comunista decide sobre propaganda")
def step_impl_communist_propaganda(context):
    """Communist strategy decides on propaganda.

    Args:
        context: Behave context object.
    """
    context.propaganda_result = context.strategy.propaganda_decision(context.policy)
    context.result = context.propaganda_result

@when("la estrategia comunista elige un revelador")
def step_impl_communist_choose_revealer(context):
    """Communist strategy chooses revealer.

    Args:
        context: Behave context object.
    """
    context.result = context.strategy.choose_revealer(context.eligible_players)


@when("la estrategia comunista decide sobre perdón")
def step_impl_communist_pardon(context):
    """Communist strategy decides on pardon.

    Args:
        context: Behave context object.
    """
    context.pardon_result = context.strategy.pardon_player()
    context.result = context.pardon_result


@when("la estrategia comunista propone veto como canciller")
def step_impl_communist_propose_veto(context):
    """Communist strategy proposes veto as chancellor.

    Args:
        context: Behave context object.
    """
    context.veto_proposal_result = context.strategy.chancellor_veto_proposal(context.policies)
    context.result = context.veto_proposal_result


@when("la estrategia comunista elige qué remover en poder socialdemócrata")
def step_impl_communist_social_democratic(context):
    """Communist strategy chooses what to remove in social democratic power.

    Args:
        context: Behave context object.
    """
    context.removal_result = context.strategy.social_democratic_removal_choice()
    context.result = context.removal_result


# Then steps (Assertions/Verification)

@then("la estrategia comunista debe estar inicializada correctamente")
def step_impl_communist_initialized(context):
    """Verify communist strategy is properly initialized.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If strategy is not properly initialized.
    """
    assert context.strategy is not None
    assert hasattr(context.strategy, "player")
    assert context.strategy.player == context.mock_player


@then("la estrategia comunista debe heredar de PlayerStrategy")
def step_impl_communist_inherits(context):
    """Verify communist strategy inherits from PlayerStrategy.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If strategy doesn't inherit from PlayerStrategy.
    """
    assert isinstance(context.strategy, PlayerStrategy)


@then("debe retornar un comunista como canciller")
def step_impl_returns_communist_chancellor(context):
    """Verify communist was chosen as chancellor.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen player is not communist.
    """
    assert context.result.is_communist == True


@then("debe priorizar comunistas al nominar")
def step_impl_prioritize_communists_nominating(context):
    """Verify communists are prioritized when nominating.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If communist was not chosen when available.
    """
    # Check that a communist was chosen when available
    communist_players = [p for p in context.eligible_players if p.is_communist]
    if communist_players:
        assert context.result.is_communist == True


@then("debe retornar el jugador liberal")
def step_impl_returns_liberal_player(context):
    """Verify liberal player was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen player is not liberal.
    """
    assert context.result.is_liberal == True


@then("debe priorizar liberales antes que fascistas")
def step_impl_prioritize_liberals_over_fascists(context):
    """Verify liberals are prioritized over fascists.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist was chosen when liberal was available.
    """
    # If no communists available, should choose liberal over fascist
    liberal_players = [p for p in context.eligible_players if p.is_liberal]
    fascist_players = [p for p in context.eligible_players if p.is_fascist]

    if liberal_players and fascist_players:
        assert context.result.is_liberal == True or context.result.is_communist == True


@then("debe mantener la política comunista (comunista)")
def step_impl_keeps_communist_policy(context):
    """Verify communist policy was kept.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If no communist policies were kept.
    """
    kept_policies, _ = context.result
    communist_policies = [p for p in kept_policies if p.type == "communist"]
    assert len(communist_policies) > 0


@then("debe descartar la política fascista (comunista)")
def step_impl_discards_fascist_policy(context):
    """Verify fascist policy was discarded.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist policy was not discarded.
    """
    if hasattr(context, "discarded") and context.discarded is not None:
        assert context.discarded.type == "fascist"
    else:
        _, discarded_policy = context.result
        assert discarded_policy.type == "fascist"


@then("debe mantener una política liberal")
def step_impl_keeps_liberal_policy(context):
    """Verify liberal policy was kept.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If no liberal policies were kept.
    """
    kept_policies, _ = context.result
    liberal_policies = [p for p in kept_policies if p.type == "liberal"]
    assert len(liberal_policies) > 0


@then("debe promulgar la política comunista (comunista)")
def step_impl_enact_communist_policy(context):
    """Verify communist policy was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen policy is not communist.
    """
    chosen, _ = context.result
    assert chosen.type == "communist"


@then("debe descartar la política liberal (comunista)")
def step_impl_discards_liberal_policy(context):
    """Verify liberal policy was discarded.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If liberal policy was not discarded.
    """
    if hasattr(context, "discarded") and context.discarded is not None:
        assert context.discarded.type == "liberal"
    else:
        _, discarded_policy = context.result
        assert discarded_policy.type == "liberal"


@then("debe promulgar la política liberal (comunista)")
def step_impl_enact_liberal_policy(context):
    """Verify liberal policy was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen policy is not liberal.
    """
    chosen, _ = context.result
    assert chosen.type == "liberal"


@then("debe votar positivamente para comunistas")
def step_impl_vote_positively_communists(context):
    """Verify positive vote for communist government.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If vote result is not True.
    """
    assert context.vote_result == True


@then("debe votar negativamente contra fascistas")
def step_impl_vote_negatively_fascists(context):
    """Verify negative vote against fascist government.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If vote result is not False.
    """
    assert context.vote_result == False


@then("debe proponer veto sin comunistas")
def step_impl_propose_veto_no_communists(context):
    """Verify veto is proposed when no communist policies available.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If veto is not proposed when it should be.
    """
    assert context.veto_result == True


@then("no debe proponer veto con comunistas")
def step_impl_no_veto_with_communists(context):
    """Verify veto is not proposed when communist policies are available.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If veto is proposed when communist policies exist.
    """
    assert context.veto_result == False


@then("debe elegir el jugador fascista conocido (comunista)")
def step_impl_choose_known_fascist(context):
    """Verify known fascist was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen player is not a known fascist.
    """
    chosen_id = context.result.id
    assert chosen_id in context.mock_player.inspected_players
    assert context.mock_player.inspected_players[chosen_id] == "fascist"


@then("debe priorizar fascistas para ejecución")
def step_impl_prioritize_fascists_execution(context):
    """Verify fascists are prioritized for execution.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist was not chosen when available.
    """
    # Check that a fascist was chosen when available
    fascist_players = [p for p in context.eligible_players if p.is_fascist]
    if fascist_players:
        assert context.result.is_fascist == True


@then("debe elegir el jugador liberal conocido (comunista)")
def step_impl_choose_known_liberal(context):
    """Verify known liberal was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen player is not a known liberal.
    """
    chosen_id = context.result.id
    assert chosen_id in context.mock_player.inspected_players
    assert context.mock_player.inspected_players[chosen_id] == "liberal"


@then("debe usar mismo criterio que ejecución")
def step_impl_same_criteria_as_execution(context):
    """Verify marking uses same criteria as execution.

    This is primarily a documentation step to ensure marking logic
    follows the same prioritization as execution logic.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist was not chosen when available.
    """
    # Check that a fascist was chosen when available
    fascist_players = [p for p in context.eligible_players if p.is_fascist]
    if fascist_players:
        assert context.result.is_fascist == True


@then("debe elegir un jugador no comunista no inspeccionado")
def step_impl_choose_non_communist_uninspected(context):
    """Verify non-communist uninspected player was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen player is communist or already inspected.
    """
    chosen_id = context.result.id

    # Should not be communist
    assert context.result.is_communist == False

    # Should not be inspected
    assert chosen_id not in context.mock_player.inspected_players


@then("debe descartar la política fascista en propaganda (comunista)")
def step_impl_discard_fascist_propaganda(context):
    """Verify fascist policy is discarded in propaganda.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist policy is not discarded.
    """
    assert context.propaganda_result == True


@then("no debe descartar la política comunista")
def step_impl_keep_communist_policy_propaganda(context):
    """Verify communist policy is not discarded in propaganda.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If communist policy is discarded.
    """
    assert context.propaganda_result == False


@then("debe elegir el jugador comunista")
def step_impl_choose_communist_player(context):
    """Verify communist player was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chosen player is not communist.
    """
    assert context.result.is_communist == True


@then("debe perdonar al comunista")
def step_impl_pardon_communist(context):
    """Verify communist was pardoned.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If communist was not pardoned or wrong player marked.
    """
    assert context.pardon_result == True
    assert context.mock_player.state.marked_for_execution.is_communist == True


@then("no debe perdonar al fascista")
def step_impl_no_pardon_fascist(context):
    """Verify fascist was not pardoned.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist was pardoned or wrong player marked.
    """
    assert context.pardon_result == False
    assert context.mock_player.state.marked_for_execution.is_fascist == True


@then("debe proponer veto sin opciones comunistas")
def step_impl_propose_veto_no_communist_options(context):
    """Verify veto is proposed when no communist options available.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If veto is not proposed when no communist options exist.
    """
    assert context.veto_proposal_result == True


@then("debe votar para promulgar la política comunista")
def step_impl_vote_enact_communist_policy(context):
    """Verify vote to enact communist policy.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If vote is negative or wrong policy type.
    """
    assert context.result == True
    assert context.mock_player.state.last_discarded.type == "communist"


@then("no debe votar para promulgar la política fascista (comunista)")
def step_impl_no_vote_enact_fascist_policy(context):
    """Verify no vote to enact fascist policy.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If vote is positive or wrong policy type.
    """
    assert context.result == False
    assert context.mock_player.state.last_discarded.type == "fascist"


@then("debe elegir remover del track fascista (comunista)")
def step_impl_remove_fascist_track(context):
    """Verify fascist track removal was chosen.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist track was not chosen for removal.
    """
    assert context.removal_result == "fascist"


@then("debe debilitar a los fascistas primero")
def step_impl_weaken_fascists_first(context):
    """Verify fascists are targeted first for weakening.

    This is primarily a documentation step to ensure the strategy
    prioritizes weakening fascist positions over other factions.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascist track was not chosen for removal.
    """
    assert context.removal_result == "fascist"


@then("debe retornar {count:d} políticas para pasar")
def step_impl_policy_count(context, count):
    """Verify correct number of policies to pass.

    Args:
        context: Behave context object.
        count (int): Expected number of policies.

    Raises:
        AssertionError: If wrong number of policies were kept.
    """
    kept_policies, _ = context.result
    assert len(kept_policies) == count
