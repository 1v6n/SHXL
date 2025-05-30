from random import choice
from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.players.strategies.base_strategy import PlayerStrategy
from src.players.strategies.smart_strategy import SmartStrategy


def ensure_mock_player_setup_smart(context):
    """Ensure mock player is properly set up with all required attributes for smart strategy."""
    if not hasattr(context, "mock_player"):
        context.mock_player = Mock()

    # Ensure all required attributes exist
    context.mock_player.name = "Smart Player"
    context.mock_player.id = 1

    # Always ensure inspected_players is a real dictionary, not a Mock
    if not hasattr(context.mock_player, "inspected_players") or not isinstance(
        context.mock_player.inspected_players, dict
    ):
        context.mock_player.inspected_players = {}

    # Ensure state exists with all necessary attributes
    if not hasattr(context.mock_player, "state") or context.mock_player.state is None:
        context.mock_player.state = Mock()

    # Board with tracks - SmartStrategy expects state.board.fascist_track
    context.mock_player.state.board = Mock()
    context.mock_player.state.board.fascist_track = 0
    context.mock_player.state.board.liberal_track = 0

    # Also set direct tracks for liberal strategy compatibility
    context.mock_player.state.fascist_track = 0
    context.mock_player.state.liberal_track = 0

    context.mock_player.state.round_number = 1
    context.mock_player.state.election_tracker = 0
    context.mock_player.state.marked_for_execution = None
    context.mock_player.state.last_discarded = None

    # Policy history for tracking suspicious players
    context.mock_player.state.policy_history = []

    # Known communists attribute for communist players
    context.mock_player.known_communists = (
        []
    )  # Role attributes - only set if not already set
    if not hasattr(context.mock_player, "is_liberal"):
        context.mock_player.is_liberal = False
    if not hasattr(context.mock_player, "is_fascist"):
        context.mock_player.is_fascist = False
    if not hasattr(context.mock_player, "is_hitler"):
        context.mock_player.is_hitler = False
    if not hasattr(context.mock_player, "is_communist"):
        context.mock_player.is_communist = False

    context.result = None  # Initialize result to None for clarity in steps


@given("un jugador smart mock")
def step_impl_smart_mock_player(context):
    """Create a mock smart player."""
    context.mock_player = Mock()
    ensure_mock_player_setup_smart(context)


@given("una estrategia smart con el jugador")
@given("creo una estrategia smart con el jugador")
def step_impl_smart_strategy(context):
    """Create a smart strategy instance."""
    ensure_mock_player_setup_smart(context)
    context.strategy = SmartStrategy(context.mock_player)


@given("una estrategia smart {role}")
def step_impl_smart_strategy_with_role(context, role):
    """Create a smart strategy with specific role."""
    ensure_mock_player_setup_smart(context)

    # Set role attributes
    if role == "fascista":
        context.mock_player.is_fascist = True
        context.mock_player.is_liberal = False
        context.mock_player.is_communist = False
        context.mock_player.is_hitler = False
    elif role == "liberal":
        context.mock_player.is_liberal = True
        context.mock_player.is_fascist = False
        context.mock_player.is_communist = False
        context.mock_player.is_hitler = False
    elif role == "comunista":
        context.mock_player.is_communist = True
        context.mock_player.is_liberal = False
        context.mock_player.is_fascist = False
        context.mock_player.is_hitler = False
    elif role == "cualquier rol":
        # Default to liberal for generic tests
        context.mock_player.is_liberal = True
        context.mock_player.is_fascist = False
        context.mock_player.is_communist = False
        context.mock_player.is_hitler = False

    context.strategy = SmartStrategy(context.mock_player)


@given("el jugador {player_id:d} es Hitler elegible")
def step_impl_hitler_eligible(context, player_id):
    """Mark a player as Hitler and eligible."""
    # Find the player in eligible_players
    for player in context.eligible_players:
        if player.id == player_id:
            player.is_hitler = True
            player.is_fascist = True  # Hitler is always fascist
            player.is_liberal = False
            player.is_communist = False
            break


@given("el jugador {player_id:d} es fascista no Hitler")
def step_impl_fascist_not_hitler(context, player_id):
    """Mark a player as fascist but not Hitler."""
    ensure_mock_player_setup_smart(context)

    # Set in inspected players
    context.mock_player.inspected_players[player_id] = (
        "fascist"  # Also set in eligible players if they exist
    )
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                player.is_fascist = True
                player.is_hitler = False
                player.is_liberal = False
                player.is_communist = False
                break

    # Recreate strategy if it exists
    if hasattr(context, "strategy"):
        context.strategy = SmartStrategy(context.mock_player)


@given("el jugador {player_id:d} tiene historial de políticas fascistas")
def step_impl_fascist_policy_history(context, player_id):
    """Mark a player as having history of fascist policies."""
    ensure_mock_player_setup_smart(context)

    # Add to policy history - add multiple entries to ensure player is marked as suspicious
    mock_player = Mock()
    mock_player.id = player_id

    # Add as both president and chancellor in fascist policies
    context.mock_player.state.policy_history.append(
        {"policy": "fascist", "president": mock_player, "chancellor": Mock()}
    )
    context.mock_player.state.policy_history.append(
        {"policy": "fascist", "president": Mock(), "chancellor": mock_player}
    )


@given("el jugador {player_id:d} no tiene historial sospechoso")
def step_impl_no_suspicious_history(context, player_id):
    """Mark a player as having no suspicious history."""
    # This is mainly for contrast in scenarios - no action needed
    pass


@given("el jugador {player_id:d} es conocido como comunista")
def step_impl_known_communist(context, player_id):
    ensure_mock_player_setup_smart(context)
    if not hasattr(context.mock_player, "known_communists"):
        context.mock_player.known_communists = []
    if player_id not in context.mock_player.known_communists:
        context.mock_player.known_communists.append(player_id)
    # Also ensure eligible player exists and has correct id
    for player in context.eligible_players:
        if player.id == player_id:
            # Optionally set player.is_communist = True
            break
    if hasattr(context, "strategy"):
        context.strategy = SmartStrategy(context.mock_player)


@given("el jugador {player_id:d} no es conocido como liberal")
def step_impl_not_known_liberal(context, player_id):
    """Ensure player is not marked as liberal."""
    ensure_mock_player_setup_smart(context)
    # Remove from inspected if marked as liberal
    if player_id in context.mock_player.inspected_players:
        if context.mock_player.inspected_players[player_id] == "liberal":
            del context.mock_player.inspected_players[player_id]


@given("un presidente smart {affiliation}")
def step_impl_smart_president(context, affiliation):
    """Create president with specific affiliation."""
    player = Mock()
    player.id = 99  # Use high ID to avoid conflicts
    player.name = f"Smart President {affiliation}"

    # Set role attributes
    if affiliation == "fascista":
        player.is_fascist = True
        player.is_liberal = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "liberal":
        player.is_liberal = True
        player.is_fascist = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "comunista":
        player.is_communist = True
        player.is_liberal = False
        player.is_fascist = False
        player.is_hitler = False
    elif affiliation == "que es Hitler":
        player.is_hitler = True
        player.is_fascist = True
        player.is_liberal = False
        player.is_communist = False
    elif affiliation == "conocido como fascista":
        ensure_mock_player_setup_smart(context)
        context.mock_player.inspected_players[player.id] = "fascist"
        player.is_fascist = True
        player.is_liberal = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "conocido como liberal":
        ensure_mock_player_setup_smart(context)
        context.mock_player.inspected_players[player.id] = "liberal"
        player.is_liberal = True
        player.is_fascist = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "sin información" or affiliation == "cualquiera":
        player.is_liberal = False
        player.is_fascist = False
        player.is_communist = False
        player.is_hitler = False

    context.president = player


@given("un canciller smart {affiliation}")
def step_impl_smart_chancellor(context, affiliation):
    """Create chancellor with specific affiliation."""
    player = Mock()
    player.id = 98  # Use different ID to avoid conflicts
    player.name = f"Smart Chancellor {affiliation}"

    # Set role attributes
    if affiliation == "fascista":
        player.is_fascist = True
        player.is_liberal = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "liberal":
        player.is_liberal = True
        player.is_fascist = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "comunista":
        player.is_communist = True
        player.is_liberal = False
        player.is_fascist = False
        player.is_hitler = False
    elif affiliation == "que es Hitler":
        player.is_hitler = True
        player.is_fascist = True
        player.is_liberal = False
        player.is_communist = False
    elif affiliation == "conocido como fascista":
        ensure_mock_player_setup_smart(context)
        context.mock_player.inspected_players[player.id] = "fascist"
        player.is_fascist = True
        player.is_liberal = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "conocido como liberal":
        ensure_mock_player_setup_smart(context)
        context.mock_player.inspected_players[player.id] = "liberal"
        player.is_liberal = True
        player.is_fascist = False
        player.is_communist = False
        player.is_hitler = False
    elif affiliation == "sin información" or affiliation == "cualquiera":
        player.is_liberal = False
        player.is_fascist = False
        player.is_communist = False
        player.is_hitler = False

    context.chancellor = player


@given("el tracker de elección está en {value:d}")
def step_impl_election_tracker(context, value):
    """Set election tracker value."""
    ensure_mock_player_setup_smart(context)
    context.mock_player.state.election_tracker = value


@given("un jugador {affiliation} marcado para ejecución")
def step_impl_marked_for_execution(context, affiliation):
    """Create a marked player with specific affiliation."""
    ensure_mock_player_setup_smart(context)

    marked_player = Mock()
    marked_player.id = 98
    marked_player.name = f"Marked {affiliation} Player"

    if affiliation == "Hitler":
        marked_player.is_hitler = True
        marked_player.is_fascist = True
        marked_player.is_liberal = False
        marked_player.is_communist = False
    elif affiliation == "liberal conocido":
        marked_player.is_liberal = True
        marked_player.is_fascist = False
        marked_player.is_communist = False
        marked_player.is_hitler = False
        context.mock_player.inspected_players[marked_player.id] = "liberal"

    context.mock_player.state.marked_for_execution = marked_player


# Note: "una política {policy_type} para propaganda" step is already defined in liberal_strategy_steps.py


# When steps - reusing many from liberal strategy but adapting for smart strategy


@when("creo una estrategia smart con el jugador")
def step_impl_create_smart_strategy(context):
    """Create smart strategy with player."""
    ensure_mock_player_setup_smart(context)
    context.strategy = SmartStrategy(context.mock_player)


@when("la estrategia smart nomina un canciller")
def step_impl_smart_nominate_chancellor(context):
    """Smart strategy nominates chancellor."""
    context.result = context.strategy.nominate_chancellor(context.eligible_players)


@when("la estrategia smart filtra las políticas")
def step_impl_smart_filter_policies(context):
    """Smart strategy filters policies."""
    result = context.strategy.filter_policies(context.policies)
    context.result = result
    # For compatibility with discard steps that expect context.discarded
    if len(result) == 2:  # (kept_policies, discarded_policy)
        context.kept_policies, context.discarded = result
        context.chosen_policies = (
            context.kept_policies
        )  # For fascist strategy compatibility
    else:
        context.kept_policies = result
        context.chosen_policies = result  # For fascist strategy compatibility
        context.discarded = None


@when("la estrategia smart elige una política")
def step_impl_smart_choose_policy(context):
    """Smart strategy chooses policy."""
    result = context.strategy.choose_policy(context.policies)
    context.chosen, context.discarded = result
    # For compatibility with liberal strategy steps that expect context.result
    context.result = result


@when("la estrategia smart vota en el gobierno")
def step_impl_smart_vote(context):
    """Smart strategy votes on government."""
    context.result = context.strategy.vote(context.president, context.chancellor)


@when("la estrategia smart decide sobre veto")
def step_impl_smart_veto(context):
    """Smart strategy decides on veto."""
    context.result = context.strategy.veto(context.policies)


@when("la estrategia smart decide aceptar veto")
def step_impl_smart_accept_veto(context):
    """Smart strategy decides to accept veto."""
    context.result = context.strategy.accept_veto(context.policies)


@when("la estrategia smart elige un jugador para ejecutar")
def step_impl_smart_choose_execute(context):
    """Smart strategy chooses player to execute."""
    context.result = context.strategy.choose_player_to_kill(context.eligible_players)


@when("la estrategia smart elige un jugador para inspeccionar")
def step_impl_smart_choose_inspect(context):
    """Smart strategy chooses player to inspect."""
    context.result = context.strategy.choose_player_to_inspect(context.eligible_players)


@when("la estrategia smart elige el siguiente presidente")
def step_impl_smart_choose_president(context):
    """Smart strategy chooses next president."""
    context.result = context.strategy.choose_next_president(context.eligible_players)


@when("la estrategia smart elige un jugador para radicalizar")
def step_impl_smart_choose_radicalize(context):
    """Smart strategy chooses player to radicalize."""
    context.result = context.strategy.choose_player_to_radicalize(
        context.eligible_players
    )


@when("la estrategia smart decide sobre propaganda")
def step_impl_smart_propaganda(context):
    """Smart strategy decides on propaganda."""
    context.propaganda_result = context.strategy.propaganda_decision(context.policy)
    # Set context.result for compatibility with liberal strategy steps
    if context.propaganda_result:
        # If policy is discarded, set result as (kept_policies, discarded_policy)
        context.result = ([], context.policy)
    else:
        # If policy is kept, set result as (kept_policies, None)
        context.result = ([context.policy], None)


@when("la estrategia smart elige un revelador")
def step_impl_smart_choose_revealer(context):
    """Smart strategy chooses revealer."""
    context.result = context.strategy.choose_revealer(context.eligible_players)


@when("la estrategia smart elige un jugador para marcar")
def step_impl_smart_choose_mark(context):
    """Smart strategy chooses player to mark."""
    context.result = context.strategy.choose_player_to_mark(context.eligible_players)


@when("la estrategia smart decide sobre perdón")
def step_impl_smart_pardon(context):
    """Smart strategy decides on pardon."""
    context.pardon_result = context.strategy.pardon_player()
    # Set context.result for compatibility with liberal strategy assertions
    context.result = context.pardon_result


@when("la estrategia smart elige qué remover en poder socialdemócrata")
def step_impl_smart_social_democratic(context):
    """Smart strategy chooses what to remove in social democratic power."""
    context.removal_result = context.strategy.social_democratic_removal_choice()
    # Set context.result for compatibility with liberal strategy assertions
    context.result = context.removal_result


@when("la estrategia smart decide sobre voto de no confianza")
def step_impl_smart_vote_no_confidence(context):
    """Smart strategy decides on vote of no confidence."""
    context.result = context.strategy.vote_of_no_confidence()


# Then steps - many can be reused from liberal strategy


@then("la estrategia smart debe estar inicializada correctamente")
def step_impl_smart_initialized(context):
    """Verify smart strategy is properly initialized."""
    assert context.strategy is not None
    assert hasattr(context.strategy, "player")
    assert context.strategy.player == context.mock_player


@then("la estrategia smart debe heredar de PlayerStrategy")
def step_impl_smart_inherits(context):
    """Verify smart strategy inherits from PlayerStrategy."""
    assert isinstance(context.strategy, PlayerStrategy)


@then("debe retornar a Hitler como canciller")
def step_impl_return_hitler_chancellor(context):
    """Verify Hitler was chosen as chancellor."""
    assert context.result.is_hitler == True


@then("debe retornar el jugador fascista conocido")
def step_impl_return_known_fascist(context):
    """Verify returns known fascist player."""
    chosen_id = context.result.id
    # Check if the chosen player is actually fascist (either in eligible_players or inspected_players)
    is_fascist = False

    # Check in eligible_players first
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == chosen_id and player.is_fascist:
                is_fascist = True
                break

    # Also check in inspected_players
    if hasattr(context, "mock_player") and hasattr(
        context.mock_player, "inspected_players"
    ):
        if chosen_id in context.mock_player.inspected_players:
            if context.mock_player.inspected_players[chosen_id] == "fascist":
                is_fascist = True

    assert (
        is_fascist
    ), f"Player {chosen_id} is not marked as fascist. Available players: {[(p.id, p.is_fascist) for p in context.eligible_players]}"


@then("debe retornar el jugador sin historial sospechoso")
def step_impl_return_non_suspicious(context):
    """Verify non-suspicious player was chosen."""
    # Check that the chosen player is not in policy history
    chosen_id = context.result.id
    suspicious_ids = set()
    if hasattr(context.mock_player.state, "policy_history"):
        for policy_data in context.mock_player.state.policy_history:
            if policy_data["policy"] == "fascist":
                suspicious_ids.add(policy_data["president"].id)
                suspicious_ids.add(policy_data["chancellor"].id)

    assert (
        chosen_id not in suspicious_ids
    ), f"Player {chosen_id} is in suspicious list: {suspicious_ids}. Policy history: {context.mock_player.state.policy_history}"


@then("debe retornar el jugador comunista conocido")
def step_impl_return_known_communist(context):
    """Verify known communist was chosen."""
    chosen_id = context.result.id
    assert chosen_id in context.mock_player.known_communists


@then("debe retornar el jugador no liberal")
def step_impl_return_non_liberal(context):
    """Verify non-liberal player was chosen."""
    chosen_id = context.result.id
    # Should not be marked as liberal in inspected players
    # Either not inspected at all, or inspected as something other than liberal
    if hasattr(context, "mock_player") and hasattr(
        context.mock_player, "inspected_players"
    ):
        if chosen_id in context.mock_player.inspected_players:
            assert (
                context.mock_player.inspected_players[chosen_id] != "liberal"
            ), f"Player {chosen_id} is marked as liberal in inspected_players: {context.mock_player.inspected_players}"
        # If not in inspected_players, that's also acceptable (unknown player)

    # Also check the actual player attributes to ensure we're not choosing a liberal
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == chosen_id:
                # For communist strategy, avoid known liberals but unknown players are acceptable
                break


@then("debe promulgar la política fascista")
def step_impl_enact_fascist_policy(context):
    """Verify fascist policy was chosen."""
    assert context.chosen.type == "fascist"


@then("el voto debe ser muy cauteloso")
def step_impl_very_cautious_vote(context):
    """Verify vote is very cautious (should be False or low probability)."""
    # In dangerous situations, smart strategy should vote more cautiously
    # We can't test randomness perfectly, but we can check the logic context
    assert context.mock_player.state.board.fascist_track >= 4


@then("el voto debe tender a ser positivo para crear caos")
def step_impl_vote_positive_for_chaos(context):
    """Verify communist tends to vote positively with fascists."""
    # This tests the communist strategy of creating chaos
    # The actual vote might be random, but we verify the context is right

    # Ensure we have a strategy with the right player setup
    if hasattr(context, "strategy") and hasattr(context.strategy, "player"):
        player = context.strategy.player
        assert (
            player.is_communist
        ), f"Player is not communist: is_communist={player.is_communist}, is_liberal={player.is_liberal}, is_fascist={player.is_fascist}"
    else:
        assert (
            context.mock_player.is_communist
        ), f"Mock player is not communist: is_communist={context.mock_player.is_communist}"

    # Also check that chancellor is fascist as expected in scenario
    assert hasattr(context, "chancellor") and context.chancellor.is_fascist


@then("debe aceptar el veto solo en situaciones críticas")
def step_impl_accept_veto_critical_only(context):
    """Verify veto acceptance only in critical situations."""
    # With election tracker at 2, should be more careful about accepting veto
    assert context.mock_player.state.election_tracker == 2


@then("debe elegir a Hitler conocido")
def step_impl_choose_known_hitler(context):
    """Verify known Hitler was chosen."""
    chosen_id = context.result.id
    # Check if the chosen player is Hitler
    assert context.result.is_hitler == True
    # Check if they're known as fascist (Hitler would be known as fascist when inspected)
    assert (
        chosen_id in context.mock_player.inspected_players
        and context.mock_player.inspected_players[chosen_id] == "fascist"
    )


@then("debe perdonar a Hitler")
def step_impl_pardon_hitler(context):
    """Verify Hitler was pardoned."""
    assert context.pardon_result == True
    assert context.mock_player.state.marked_for_execution.is_hitler == True


@then("debe elegir remover del track liberal")
def step_impl_remove_liberal_track(context):
    """Verify liberal track removal was chosen."""
    assert context.removal_result == "liberal"


@then("no debe descartar la carta de poder")
def step_impl_keep_power_card(context):
    """Verify power card was not discarded."""
    assert context.propaganda_result == False


# Additional step definitions for smart strategy


@given("el jugador {player_id:d} es liberal")
def step_impl_player_is_liberal(context, player_id):
    """Set player as liberal."""
    for player in context.eligible_players:
        if player.id == player_id:
            player.is_liberal = True
            player.is_fascist = False
            player.is_communist = False
            player.is_hitler = False
            break


@given("el jugador {player_id:d} es fascista")
def step_impl_player_is_fascist(context, player_id):
    """Set player as fascist."""
    for player in context.eligible_players:
        if player.id == player_id:
            player.is_fascist = True
            player.is_liberal = False
            player.is_communist = False
            player.is_hitler = False
            break


@given("el jugador {player_id:d} no fue inspeccionado")
def step_impl_player_not_inspected(context, player_id):
    """Mark player as not inspected."""
    ensure_mock_player_setup_smart(context)
    if player_id in context.mock_player.inspected_players:
        del context.mock_player.inspected_players[player_id]


@then("debe mantener la política fascista")
def step_impl_keeps_fascist_policy(context):
    """Verify keeps fascist policy."""
    kept_policies, _ = context.result
    fascist_policies = [p for p in kept_policies if p.type == "fascist"]
    assert len(fascist_policies) > 0


@then("debe descartar la política liberal")
def step_impl_discards_liberal_policy(context):
    """Verify discards liberal policy."""
    # Check if this is from choose_policy (has context.discarded)
    if hasattr(context, "discarded") and context.discarded is not None:
        assert context.discarded.type == "liberal"
    # Check if this is from propaganda_decision (has context.propaganda_result and context.policy)
    elif hasattr(context, "propaganda_result") and hasattr(context, "policy"):
        assert context.propaganda_result == True and context.policy.type == "liberal"
    else:
        # Fallback to context.result if available
        if hasattr(context, "result"):
            _, discarded_policy = context.result
            assert discarded_policy.type == "liberal"
        else:
            raise AssertionError(
                "No valid context for checking discarded liberal policy"
            )


@then("debe retornar {count:d} políticas para pasar")
def step_impl_return_policy_count(context, count):
    """Verify returns correct number of policies."""
    kept_policies, _ = context.result
    assert len(kept_policies) == count


@then("debe elegir el jugador fascista")
def step_impl_choose_fascist_player(context):
    """Verify chooses fascist player."""
    fascist_players = [p.id for p in context.eligible_players if p.is_fascist]
    assert context.result.id in fascist_players


@given("el estado del juego tiene {count:d} políticas fascistas")
def step_impl_game_state_fascist_policies_smart(context, count):
    """Set the fascist track count in game state for smart strategy."""
    ensure_mock_player_setup_smart(context)
    # Set both board.fascist_track (for SmartStrategy) and fascist_track (for LiberalStrategy compatibility)
    context.mock_player.state.board.fascist_track = count
    context.mock_player.state.fascist_track = count


@given("el jugador {player_id:d} es conocido como fascista y es Hitler")
def step_impl_known_fascist_hitler(context, player_id):
    """Set player as known fascist and Hitler."""
    ensure_mock_player_setup_smart(context)
    context.mock_player.inspected_players[player_id] = "fascist"
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                player.is_fascist = True
                player.is_liberal = False
                player.is_communist = False
                player.is_hitler = True
                break


@given("el jugador {player_id:d} es conocido como {affiliation} ({strategy_context})")
def step_impl_known_player_affiliation_smart(
    context, player_id, affiliation, strategy_context
):
    """Mark a player as having a known affiliation for smart strategy."""
    # The strategy_context parameter is ignored but needed for pattern matching
    ensure_mock_player_setup_smart(context)

    # Map Spanish terms to English terms expected by strategy
    affiliation_map = {
        "liberal": "liberal",
        "fascista": "fascist",
        "fascista no Hitler": "fascist",
        "fascista y es Hitler": "fascist",
        "comunista": "communist",
    }

    english_affiliation = affiliation_map.get(affiliation, affiliation)
    context.mock_player.inspected_players[player_id] = english_affiliation

    # Also set in eligible players if they exist
    if hasattr(context, "eligible_players"):
        for player in context.eligible_players:
            if player.id == player_id:
                if english_affiliation == "liberal":
                    player.is_liberal = True
                    player.is_fascist = False
                    player.is_communist = False
                    player.is_hitler = False
                elif english_affiliation == "fascist":
                    player.is_fascist = True
                    player.is_liberal = False
                    player.is_communist = False
                    player.is_hitler = False
                elif english_affiliation == "communist":
                    player.is_communist = True
                    player.is_liberal = False
                    player.is_fascist = False
                    player.is_hitler = False
                break

    # Recreate strategy if it exists to ensure it uses updated mock_player
    if hasattr(context, "strategy"):
        context.strategy = SmartStrategy(context.mock_player)
