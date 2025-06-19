import ast
from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when
from src.game.board import GameBoard
from src.policies.policy import Communist, Fascist, Liberal
from src.policies.policy_factory import PolicyFactory

# Note: The steps "una partida de {player_count:d} jugadores" and "la opción comunistas está {status}"
# are already defined in policy_deck_steps.py


@given("un tablero inicializado")
def step_impl_board_initialized(context):
    """Initialize a GameBoard with a mock game state."""
    context.game_state = Mock()
    context.game_state.game_over = False
    context.game_state.winner = None
    context.game_state.fascist_track = 0
    context.game_state.communist_track = 0
    context.game_state.block_next_fascist_power = False
    context.game_state.block_next_communist_power = False
    context.game_state.most_recent_policy = None
    context.game_state.enacted_policies = 0
    context.game_state.round_number = 1
    context.game_state.president = Mock()
    context.game_state.chancellor = Mock()
    context.game_state.president.name = "President"
    context.game_state.chancellor.name = "Chancellor"

    context.board = GameBoard(
        context.game_state, context.player_count, context.with_communists
    )

    # Set the board reference in the game state to point to the actual board
    context.game_state.board = context.board


@given("un tablero inicializado con mazo de políticas")
def step_impl_board_with_policy_deck(context):
    """Initialize a GameBoard with a policy deck."""
    step_impl_board_initialized(context)
    context.board.initialize_policy_deck(PolicyFactory)
    context.initial_deck_size = len(context.board.policies)


@given("políticas en la pila de descartes")
def step_impl_policies_in_discard(context):
    """Add some policies to the discard pile."""
    test_policies = [Liberal(), Fascist(), Communist()]
    context.board.discard(test_policies)


@when("inicializo el tablero")
def step_impl_initialize_board(context):
    """Initialize the board and store it in context."""
    step_impl_board_initialized(context)


@when("promulgo {policy_count:d} políticas {policy_type}")
def step_impl_enact_policies(context, policy_count, policy_type):
    """Enact a specified number of policies of a given type."""
    policy_map = {"liberal": Liberal, "fascist": Fascist, "communist": Communist}

    context.last_power = None
    for i in range(policy_count):
        policy = policy_map[policy_type]()
        power = context.board.enact_policy(policy)
        if power:
            context.last_power = power


@when("robo {count:d} políticas")
def step_impl_draw_policies(context, count):
    """Draw policies from the deck."""
    context.drawn_policies = context.board.draw_policy(count)


@when("descarto {count:d} política")
def step_impl_discard_policies(context, count):
    """Discard a policy."""
    if hasattr(context, "drawn_policies") and context.drawn_policies:
        policies_to_discard = context.drawn_policies[:count]
        context.board.discard(policies_to_discard)


@when("robo más políticas de las disponibles en el mazo")
def step_impl_draw_more_than_available(context):
    """Draw more policies than available to trigger deck reshuffling."""
    policies_in_deck = len(context.board.policies)
    policies_needed = policies_in_deck + 3  # More than available
    context.drawn_policies = context.board.draw_policy(policies_needed)


@then("el tamaño de la pista {track_type} debe ser {expected_size:d}")
def step_impl_track_size(context, track_type, expected_size):
    """Verify track size."""
    if track_type == "liberal":
        actual_size = context.board.liberal_track_size
    elif track_type == "fascista":
        actual_size = context.board.fascist_track_size
    elif track_type == "comunista":
        actual_size = context.board.communist_track_size
    else:
        raise ValueError(f"Unknown track type: {track_type}")

    assert (
        actual_size == expected_size
    ), f"Esperaba tamaño {expected_size} para pista {track_type}, pero encontré {actual_size}"


@then("los poderes {power_type} deben ser {expected_powers}")
def step_impl_powers_setup(context, power_type, expected_powers):
    """Verify power setup."""
    # Parse the expected powers string into a list
    expected_list = ast.literal_eval(expected_powers)

    if power_type == "fascistas":
        actual_powers = context.board.fascist_powers
    elif power_type == "comunistas":
        actual_powers = context.board.communist_powers
    else:
        raise ValueError(f"Unknown power type: {power_type}")

    assert (
        actual_powers == expected_list
    ), f"Esperaba poderes {expected_list} para {power_type}, pero encontré {actual_powers}"


@then("la pista {policy_type} debe tener {expected_count:d} políticas")
def step_impl_track_count(context, policy_type, expected_count):
    """Verify track progress."""
    # Map Spanish to English policy types
    policy_type_map = {
        "liberal": "liberal",
        "fascist": "fascist",
        "fascista": "fascist",  # Spanish translation
        "communist": "communist",
        "comunista": "communist",  # Spanish translation
    }

    normalized_policy_type = policy_type_map.get(policy_type, policy_type)

    if normalized_policy_type == "liberal":
        actual_count = context.board.liberal_track
    elif normalized_policy_type == "fascist":
        actual_count = context.board.fascist_track
    elif normalized_policy_type == "communist":
        actual_count = context.board.communist_track
    else:
        raise ValueError(f"Unknown policy type: {policy_type}")

    assert (
        actual_count == expected_count
    ), f"Esperaba {expected_count} políticas en pista {policy_type}, pero encontré {actual_count}"


@then("el poder otorgado debe ser {expected_power}")
def step_impl_power_granted(context, expected_power):
    """Verify the power granted by policy enactment."""
    if expected_power == "None":
        expected_power = None
    else:
        expected_power = expected_power.strip('"')

    actual_power = getattr(context, "last_power", None)
    assert (
        actual_power == expected_power
    ), f"Esperaba poder {expected_power}, pero encontré {actual_power}"


@then("el veto debe estar {veto_status}")
def step_impl_veto_status(context, veto_status):
    """Verify veto availability."""
    expected_veto = veto_status == "disponible"
    actual_veto = context.board.veto_available

    assert (
        actual_veto == expected_veto
    ), f"Esperaba veto {veto_status}, pero encontré {'disponible' if actual_veto else 'no disponible'}"


@then("el juego debe estar {game_status}")
def step_impl_game_status(context, game_status):
    """Verify game over status."""
    expected_game_over = game_status == "terminado"
    actual_game_over = context.game_state.game_over

    assert (
        actual_game_over == expected_game_over
    ), f"Esperaba juego {game_status}, pero encontré {'terminado' if actual_game_over else 'en curso'}"


@then("el ganador debe ser {expected_winner}")
def step_impl_winner(context, expected_winner):
    """Verify the winner."""
    actual_winner = context.game_state.winner
    assert (
        actual_winner == expected_winner
    ), f"Esperaba ganador {expected_winner}, pero encontré {actual_winner}"


@then("debo tener {expected_count:d} políticas en mano")
def step_impl_policies_drawn(context, expected_count):
    """Verify number of policies drawn."""
    actual_count = (
        len(context.drawn_policies) if hasattr(context, "drawn_policies") else 0
    )
    assert (
        actual_count == expected_count
    ), f"Esperaba {expected_count} políticas en mano, pero encontré {actual_count}"


@then("el mazo debe tener menos políticas")
def step_impl_deck_reduced(context):
    """Verify that the deck has fewer policies after drawing."""
    current_deck_size = len(context.board.policies)
    assert (
        current_deck_size < context.initial_deck_size
    ), f"El mazo debería tener menos políticas que {context.initial_deck_size}, pero tiene {current_deck_size}"


@then("la pila de descartes debe tener {expected_count:d} política")
def step_impl_discard_pile_size(context, expected_count):
    """Verify discard pile size."""
    actual_count = len(context.board.discards)
    assert (
        actual_count >= expected_count
    ), f"Esperaba al menos {expected_count} políticas en descartes, pero encontré {actual_count}"


@then("el mazo debe reorganizarse incluyendo los descartes")
def step_impl_deck_reshuffled(context):
    """Verify that the deck was reshuffled with discards."""
    # After drawing more than available, the discard pile should be empty (shuffled back into deck)
    discard_count = len(context.board.discards)
    assert (
        discard_count == 0
    ), f"Esperaba pila de descartes vacía después de reorganizar, pero encontré {discard_count} políticas"


@then("debo poder robar las políticas solicitadas")
def step_impl_policies_drawn_successfully(context):
    """Verify that all requested policies were drawn successfully."""
    assert hasattr(context, "drawn_policies"), "No se robaron políticas"
    assert (
        len(context.drawn_policies) > 0
    ), "No se pudieron robar las políticas solicitadas"
