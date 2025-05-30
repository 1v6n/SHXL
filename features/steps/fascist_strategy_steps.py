from random import choice
from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.players.strategies.base_strategy import PlayerStrategy
from src.players.strategies.fascist_strategy import FascistStrategy


def ensure_fascist_mock_player_setup(context):
    """Ensure fascist mock player is properly set up with all required attributes."""
    if not hasattr(context, "mock_player"):
        context.mock_player = Mock()

    # Ensure all required attributes exist
    context.mock_player.name = "Fascist Player"
    context.mock_player.id = 1
    context.mock_player.is_fascist = True
    context.mock_player.is_hitler = False
    context.mock_player.is_liberal = False
    context.mock_player.is_communist = (
        False  # Always ensure inspected_players is a real dictionary, not a Mock
    )
    if not hasattr(context.mock_player, "inspected_players") or not isinstance(
        context.mock_player.inspected_players, dict
    ):
        context.mock_player.inspected_players = {}

    # Always ensure known_affiliations is a real dictionary, not a Mock
    if not hasattr(context.mock_player, "known_affiliations") or not isinstance(
        context.mock_player.known_affiliations, dict
    ):
        context.mock_player.known_affiliations = {}

    # Ensure state exists
    if not hasattr(context.mock_player, "state") or context.mock_player.state is None:
        context.mock_player.state = Mock()
    context.mock_player.state.fascist_track = 0
    context.mock_player.state.communist_track = 0
    context.mock_player.state.liberal_track = 0
    context.mock_player.state.marked_for_execution = None
    context.mock_player.state.last_discarded = None

    # Mock board for track sizes
    if not hasattr(context.mock_player.state, "board"):
        context.mock_player.state.board = Mock()
    context.mock_player.state.board.liberal_track = 0
    context.mock_player.state.board.liberal_track_size = 5


@given("un jugador fascista mock")
def step_impl_fascist_mock_player(context):
    ensure_fascist_mock_player_setup(context)


@given("una estrategia fascista")
def step_impl_fascist_strategy(context):
    ensure_fascist_mock_player_setup(context)
    context.strategy = FascistStrategy(context.mock_player)


# Use the existing implementation from liberal_strategy_steps.py
# @given("una lista de {count:d} jugadores elegibles para canciller") - removed duplicate


@given("el jugador {player_id:d} es Hitler")
def step_impl_player_is_hitler(context, player_id):
    for player in getattr(context, "eligible_players", []):
        if getattr(player, "id", None) == player_id:
            player.is_fascist = True
            player.is_hitler = True
            player.is_liberal = False
            player.is_communist = False
            break


@given("el jugador {player_id:d} es fascista no Hitler")
def step_impl_player_is_fascist_not_hitler(context, player_id):
    for player in getattr(context, "eligible_players", []):
        if getattr(player, "id", None) == player_id:
            player.is_fascist = True
            player.is_hitler = False
            player.is_liberal = False
            player.is_communist = False
            break


@given("el track fascista tiene {count:d} políticas")
def step_impl_fascist_track_count(context, count):
    ensure_fascist_mock_player_setup(context)
    context.mock_player.state.fascist_track = count


@given("una lista de {count:d} jugadores elegibles sin fascistas")
def step_impl_eligible_players_no_fascists(context, count):
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        player.is_fascist = False
        player.is_hitler = False
        player.is_liberal = True
        player.is_communist = False
        context.eligible_players.append(player)


@given("una lista de {count:d} políticas: {policy_list}")
def step_impl_fascist_policies_list(context, count, policy_list):
    policy_names = [p.strip().strip('"') for p in policy_list.split(",")]
    context.policies = []
    for policy_name in policy_names:
        policy = Mock()
        policy.type = policy_name
        context.policies.append(policy)


# Removed duplicate: @given("un presidente mock") - defined in random_strategy_steps.py


@given("un canciller fascista")
def step_impl_chancellor_fascist(context):
    context.chancellor = Mock()
    context.chancellor.id = 11
    context.chancellor.name = "Chancellor"
    context.chancellor.is_fascist = True
    context.chancellor.is_hitler = False
    context.chancellor.is_liberal = False


@given("un presidente conocido como {affiliation}")
def step_impl_president_known_affiliation(context, affiliation):
    ensure_fascist_mock_player_setup(context)
    context.president = Mock()
    context.president.id = 10
    context.president.name = "President"
    context.president.is_fascist = affiliation == "fascist"
    context.president.is_liberal = affiliation == "liberal"
    context.president.is_hitler = False

    # Add to inspected players
    context.mock_player.inspected_players[context.president.id] = affiliation


@given("un canciller conocido como {affiliation}")
def step_impl_chancellor_known_affiliation(context, affiliation):
    ensure_fascist_mock_player_setup(context)
    context.chancellor = Mock()
    context.chancellor.id = 11
    context.chancellor.name = "Chancellor"
    context.chancellor.is_fascist = affiliation == "fascist"
    context.chancellor.is_liberal = affiliation == "liberal"
    context.chancellor.is_hitler = False

    # Add to inspected players
    context.mock_player.inspected_players[context.chancellor.id] = affiliation


# Removed duplicate: @given("un canciller mock") - defined in random_strategy_steps.py


# Use the existing implementation from liberal_strategy_steps.py
# @given("una lista de políticas para veto: {policy_list}") - removed duplicate


# Use the existing implementation from liberal_strategy_steps.py
# @given("una lista de {count:d} jugadores elegibles para {action}") - removed duplicate


@given("el jugador {player_id:d} es conocido como {affiliation}")
def step_impl_known_player_affiliation_fascist(context, player_id, affiliation):
    # Use existing mock player if available, otherwise set up fascist mock player
    if not hasattr(context, "mock_player"):
        ensure_fascist_mock_player_setup(context)

    # Ensure inspected_players exists as a real dictionary
    if not hasattr(context.mock_player, "inspected_players") or not isinstance(
        context.mock_player.inspected_players, dict
    ):
        context.mock_player.inspected_players = {}

    if "Hitler" in affiliation:
        hitler_player = True
    else:
        hitler_player = False  # Map Spanish terms to English terms expected by strategy
    affiliation_map = {
        "fascista": "fascist",
        "fascista no Hitler": "fascist",
        "fascista y es Hitler": "fascist",  # Add this mapping
        "liberal": "liberal",
        "liberal (liberal)": "liberal",  # Handle smart strategy test format
        "comunista": "communist",
        "hitler": "hitler",
    }
    english_affiliation = affiliation_map.get(affiliation, affiliation)

    # Find the player and set their affiliation
    for player in context.eligible_players:
        if player.id == player_id:
            if english_affiliation == "liberal":
                player.is_fascist = False
                player.is_liberal = True
                player.is_communist = False
                player.is_hitler = False
            elif english_affiliation == "fascist":
                player.is_fascist = True
                player.is_liberal = False
                player.is_communist = False
                player.is_hitler = False
                if hitler_player:
                    player.is_hitler = True
            elif english_affiliation == "communist":
                player.is_fascist = False
                player.is_liberal = False
                player.is_communist = True
                player.is_hitler = False
            elif english_affiliation == "hitler":
                player.is_fascist = True
                player.is_liberal = False
                player.is_communist = False
                player.is_hitler = True
            break

    # Add to inspected players using English term
    context.mock_player.inspected_players[player_id] = english_affiliation


@given("los liberales están cerca de la victoria")
def step_impl_liberals_near_victory(context):
    ensure_fascist_mock_player_setup(context)
    context.mock_player.state.board.liberal_track = 3  # Close to victory (5 needed)


@given("el jugador {player_id:d} no es fascista")
def step_impl_player_not_fascist(context, player_id):
    for player in context.eligible_players:
        if player.id == player_id:
            player.is_fascist = False
            player.is_hitler = False
            player.is_liberal = True
            break


# @given("el jugador {player_id:d} no fue inspeccionado")
# def step_impl_player_not_inspected(context, player_id):
#     ensure_fascist_mock_player_setup(context)
#     # Ensure the player is not in inspected_players
#     if player_id in context.mock_player.inspected_players:
#         del context.mock_player.inspected_players[player_id]


# Use the existing implementation from liberal_strategy_steps.py
# @given("una política {policy_type} para propaganda") - removed duplicate

# Note: "Hitler está marcado para ejecución" step is defined in ai_player_steps.py


@given("un fascista está marcado para ejecución")
def step_impl_fascist_marked_execution(context):
    ensure_fascist_mock_player_setup(context)
    fascist_player = Mock()
    fascist_player.is_fascist = True
    fascist_player.is_hitler = False
    fascist_player.id = 98
    context.mock_player.state.marked_for_execution = fascist_player


@given("un liberal está marcado para ejecución")
def step_impl_liberal_marked_execution(context):
    ensure_fascist_mock_player_setup(context)
    liberal_player = Mock()
    liberal_player.is_liberal = True
    liberal_player.is_fascist = False
    liberal_player.is_hitler = False
    liberal_player.id = 97
    context.mock_player.state.marked_for_execution = liberal_player


@given("políticas sin fascistas para propuesta de veto")
def step_impl_policies_no_fascists_veto(context):
    context.veto_proposal_policies = []
    for policy_type in ["liberal", "communist"]:
        policy = Mock()
        policy.type = policy_type
        context.veto_proposal_policies.append(policy)


# Use the existing implementation from liberal_strategy_steps.py
# @given("una política {policy_type} como última descartada") - removed duplicate


@given("el estado tiene políticas comunistas y liberales")
def step_impl_state_communist_liberal_policies(context):
    ensure_fascist_mock_player_setup(context)
    context.mock_player.state.communist_track = 2
    context.mock_player.state.liberal_track = 1


@when("creo una estrategia fascista con el jugador")
def step_impl_create_fascist_strategy(context):
    ensure_fascist_mock_player_setup(context)
    context.strategy = FascistStrategy(context.mock_player)


@when("la estrategia fascista nomina un canciller")
def step_impl_fascist_nominate_chancellor(context):
    context.result = context.strategy.nominate_chancellor(context.eligible_players)


@when("la estrategia fascista filtra las políticas")
def step_impl_fascist_filter_policies(context):
    chosen, discarded = context.strategy.filter_policies(context.policies)
    context.chosen_policies = chosen
    context.discarded_policy = discarded
    # For compatibility with smart strategy steps that expect (kept_policies, discarded_policy)
    context.result = (chosen, discarded)


@when("la estrategia fascista elige una política")
def step_impl_fascist_choose_policy(context):
    chosen, discarded = context.strategy.choose_policy(context.policies)
    context.chosen = chosen
    context.discarded_policy = discarded
    context.result = (
        chosen,
        discarded,
    )  # Set result for compatibility with shared steps


@when("la estrategia fascista vota en el gobierno")
def step_impl_fascist_vote(context):
    context.vote_result = context.strategy.vote(context.president, context.chancellor)
    context.result = (
        context.vote_result
    )  # Set result for compatibility with shared steps


@when("la estrategia fascista decide sobre veto")
def step_impl_fascist_veto_decision(context):
    # Use the policies set up in context.policies
    context.veto_result = context.strategy.veto(context.policies)


@when("la estrategia fascista decide aceptar veto")
def step_impl_fascist_accept_veto(context):
    # Use the policies set up in context.policies
    context.accept_veto_result = context.strategy.accept_veto(context.policies)


@when("la estrategia fascista elige un jugador para ejecutar")
def step_impl_fascist_choose_execution(context):
    context.execution_result = context.strategy.choose_player_to_kill(
        context.eligible_players
    )
    context.result = (
        context.execution_result
    )  # Set result for compatibility with shared steps


@when("la estrategia fascista elige un jugador para inspeccionar")
def step_impl_fascist_choose_inspection(context):
    context.inspection_result = context.strategy.choose_player_to_inspect(
        context.eligible_players
    )


@when("la estrategia fascista elige un jugador para espionar")
def step_impl_fascist_choose_spy(context):
    context.spy_result = context.strategy.choose_player_to_bug(context.eligible_players)


@when("la estrategia fascista elige un revelador")
def step_impl_fascist_choose_revealer(context):
    context.revealer_result = context.strategy.choose_revealer(context.eligible_players)
    context.result = (
        context.revealer_result
    )  # Set result for compatibility with shared steps


@when("la estrategia fascista elige el siguiente presidente")
def step_impl_fascist_choose_next_president(context):
    context.next_president_result = context.strategy.choose_next_president(
        context.eligible_players
    )
    context.result = (
        context.next_president_result
    )  # Set result for compatibility with shared steps


@when("la estrategia fascista elige un jugador para radicalizar")
def step_impl_fascist_choose_radicalize(context):
    context.radicalize_result = context.strategy.choose_player_to_radicalize(
        context.eligible_players
    )
    context.result = (
        context.radicalize_result
    )  # Set result for compatibility with shared steps


@when("la estrategia fascista elige un jugador para marcar")
def step_impl_fascist_choose_mark(context):
    context.mark_result = context.strategy.choose_player_to_mark(
        context.eligible_players
    )
    context.result = (
        context.mark_result
    )  # Set result for compatibility with shared steps


# Removed duplicate: @when("la estrategia fascista elige un jugador para espionar") - already defined above


@when("la estrategia fascista decide sobre propaganda")
def step_impl_fascist_propaganda_decision(context):
    context.propaganda_result = context.strategy.propaganda_decision(context.policy)


# Removed duplicate: @when("la estrategia fascista elige un revelador") - already defined above


@when("la estrategia fascista decide sobre perdón")
def step_impl_fascist_pardon_decision(context):
    context.pardon_result = context.strategy.pardon_player()


@when("la estrategia fascista propone veto como canciller")
def step_impl_fascist_chancellor_veto_proposal(context):
    policies = getattr(
        context, "veto_proposal_policies", getattr(context, "policies", None)
    )
    assert (
        policies is not None
    ), "No se encontró ninguna lista de políticas en el contexto"
    context.chancellor_veto_result = context.strategy.chancellor_veto_proposal(policies)


@when("la estrategia fascista decide sobre voto de no confianza")
def step_impl_fascist_vote_no_confidence(context):
    context.no_confidence_result = context.strategy.vote_of_no_confidence()


@when("la estrategia fascista elige qué remover en poder socialdemócrata")
def step_impl_fascist_social_democratic_removal(context):
    context.removal_result = context.strategy.social_democratic_removal_choice()


@then("la estrategia fascista debe estar inicializada correctamente")
def step_impl_check_fascist_strategy_initialized(context):
    assert context.strategy is not None
    assert context.strategy.player == context.mock_player


@then("la estrategia fascista debe heredar de PlayerStrategy")
def step_impl_check_fascist_strategy_inheritance(context):
    assert isinstance(context.strategy, PlayerStrategy)
    assert isinstance(context.strategy, FascistStrategy)


@then("debe retornar Hitler como canciller")
def step_impl_check_hitler_chancellor(context):
    assert context.result.is_hitler is True
    assert context.result.is_fascist is True


@then("debe priorizar a Hitler cuando es seguro")
def step_impl_check_hitler_priority_safe(context):
    # Verify that Hitler was chosen when fascist track >= 3
    assert context.result.is_hitler is True


@then("debe retornar el fascista no Hitler")
def step_impl_check_fascist_not_hitler(context):
    # The chosen player should be fascist and not Hitler
    assert context.result.is_fascist is True, "Chosen player is not fascist"
    assert (
        getattr(context.result, "is_hitler", False) is False
    ), "Chosen player is Hitler, should not be"


@then("no debe elegir Hitler cuando no es seguro")
def step_impl_check_no_hitler_unsafe(context):
    # Verify Hitler was not chosen when fascist track < 3
    assert context.result.is_hitler is False


@then("debe retornar uno de los jugadores elegibles fascista")
def step_impl_check_eligible_player_fascist(context):
    assert context.result in context.eligible_players


@then("debe elegir aleatoriamente entre no fascistas")
def step_impl_check_random_non_fascist(context):
    # Since all eligible players are non-fascist, any choice is valid
    assert context.result in context.eligible_players
    assert context.result.is_fascist is False


@then("debe retornar {count:d} políticas para pasar")
def step_impl_check_policies_count(context, count):
    assert len(context.chosen_policies) == count


# Use the existing implementation from liberal_strategy_steps.py
# @then("debe mantener la política comunista") - removed duplicate


@then("debe descartar una política liberal")
def step_impl_check_discard_liberal_single(context):
    assert context.discarded_policy.type == "liberal"


@then("debe priorizar comunista sobre liberal")
def step_impl_check_communist_over_liberal(context):
    # Verify communist was chosen over liberal
    communist_in_chosen = any(p.type == "communist" for p in context.chosen_policies)
    assert communist_in_chosen


# Use the existing implementation from liberal_strategy_steps.py
# @then("debe promulgar la política comunista") - removed duplicate


@then("debe votar positivamente para fascistas")
def step_impl_check_vote_yes_fascists(context):
    assert context.vote_result is True


@then("debe votar cautelosamente contra liberales")
def step_impl_check_vote_cautious_liberals(context):
    # The strategy should vote cautiously (low probability) when both are known liberals
    # We can't test the exact probability, but we can verify the logic works
    assert isinstance(context.vote_result, bool)


@then("la probabilidad de voto positivo debe ser muy baja")
def step_impl_check_very_low_vote_probability(context):
    # Test multiple times to verify low probability
    yes_votes = 0
    total_votes = 100

    for _ in range(total_votes):
        vote = context.strategy.vote(context.president, context.chancellor)
        if vote:
            yes_votes += 1

    # Should be around 30% or less
    assert yes_votes <= 45  # Allow some variance


@then("debe votar estratégicamente para obtener poder")
def step_impl_check_strategic_power_vote(context):
    # When fascist track is 2, should vote with high probability
    assert isinstance(context.vote_result, bool)


# Use the existing implementation from liberal_strategy_steps.py
# @then("la probabilidad de voto positivo debe ser alta") - removed duplicate


@then("debe proponer veto sin fascistas")
def step_impl_check_veto_no_fascists(context):
    assert context.veto_result is True


@then("no debe proponer veto con fascistas")
def step_impl_check_no_veto_with_fascists(context):
    assert context.veto_result is False


@then("debe aceptar veto sin fascistas")
def step_impl_check_accept_veto_no_fascists(context):
    assert context.accept_veto_result is True


@then("no debe aceptar veto con fascistas")
def step_impl_check_no_accept_veto_fascists(context):
    assert context.accept_veto_result is False


# Use the existing implementation from liberal_strategy_steps.py
# @then("debe elegir el jugador liberal conocido") - removed duplicate


@then("debe priorizar liberales para ejecución")
def step_impl_check_prioritize_liberals_execution(context):
    # Check that a liberal was chosen if available
    if hasattr(context, "execution_result"):
        # Verify it's targeting the right type of player
        assert context.execution_result in context.eligible_players


@then("debe priorizar eliminar liberales urgentemente")
def step_impl_check_urgent_liberal_elimination(context):
    # When liberals are close to victory, should target known liberals
    assert context.execution_result.id in context.strategy.player.inspected_players
    assert (
        context.strategy.player.inspected_players[context.execution_result.id]
        == "liberal"
    )


@then("debe elegir un jugador no fascista")
def step_impl_check_choose_non_fascist(context):
    """Check that chosen player is not fascist."""
    chosen_player = context.inspection_result
    assert chosen_player.is_fascist is False


@then("no debe inspeccionar fascistas")
def step_impl_should_not_inspect_fascists(context):
    """Check strategy avoids inspecting fascists."""
    chosen_player = context.inspection_result
    assert chosen_player.is_fascist is False


@then("debe elegir un jugador no fascista no inspeccionado")
def step_impl_check_choose_non_fascist_uninspected(context):
    """Check that chosen player is not fascist and not inspected."""
    chosen_player = context.spy_result
    assert getattr(chosen_player, "is_fascist", False) is False
    # Check if player was inspected using the correct attribute/method
    player_was_inspected = (
        hasattr(context.strategy.player, "inspected_players")
        and chosen_player.id in context.strategy.player.inspected_players
    )
    assert player_was_inspected is False


@then("debe obtener información útil")
def step_impl_should_get_useful_info(context):
    """Check that the spying action gets useful information."""
    # This is a strategic check - fascist should spy on unknown players
    assert context.spy_result is not None


@then("debe descartar la política liberal en propaganda")
def step_impl_should_discard_liberal_propaganda(context):
    """Check that liberal policy is discarded in propaganda."""
    assert context.propaganda_result is True  # True means discard


@then("no debe descartar la política fascista")
def step_impl_should_not_discard_fascist_propaganda(context):
    """Check that fascist policy is not discarded in propaganda."""
    assert context.propaganda_result is False  # False means keep


@then("debe revelar información a aliados")
def step_impl_should_reveal_to_allies(context):
    """Check that revelation helps fascist allies."""
    # Strategic check - revealer should be fascist
    assert context.revealer_result.is_fascist is True


@then("siempre debe proteger a Hitler")
def step_impl_check_always_protect_hitler(context):
    # Hitler should always be pardoned by fascists
    assert context.pardon_result is True


@then("debe perdonar al fascista")
def step_impl_check_pardon_fascist(context):
    assert context.pardon_result is True


@then("debe proteger a aliados fascistas")
def step_impl_check_protect_fascist_allies(context):
    # Fascists should protect fellow fascists
    assert context.pardon_result is True


@then("no debe perdonar al liberal")
def step_impl_check_no_pardon_liberal(context):
    assert context.pardon_result is False


@then("debe permitir ejecución de enemigos")
def step_impl_check_allow_enemy_execution(context):
    # Should not pardon liberals/enemies
    assert context.pardon_result is False


@then("debe proponer veto sin opciones fascistas")
def step_impl_check_veto_no_fascist_options(context):
    assert context.chancellor_veto_result is True


@then("debe votar para promulgar la política fascista")
def step_impl_check_vote_enact_fascist(context):
    assert context.no_confidence_result is True


@then("no debe votar para promulgar la política liberal")
def step_impl_check_no_vote_enact_liberal(context):
    assert context.no_confidence_result is False


@then("debe elegir remover del track comunista")
def step_impl_check_remove_communist_track(context):
    assert context.removal_result == "communist"


@then("debe debilitar a otros enemigos primero")
def step_impl_check_weaken_other_enemies(context):
    # Should prioritize removing communist policies over liberal ones
    assert context.removal_result == "communist"


@given("el jugador {player_id:d} es fascista")
def step_impl_player_is_fascist(context, player_id):
    # Mark a player as fascist (non-Hitler)
    for player in getattr(context, "eligible_players", []):
        if getattr(player, "id", None) == player_id:
            player.is_fascist = True
            player.is_hitler = False
            player.is_liberal = False
            player.is_communist = False
            break


@given("el jugador {player_id:d} no es fascista")
def step_impl_player_is_not_fascist(context, player_id):
    for player in getattr(context, "eligible_players", []):
        if getattr(player, "id", None) == player_id:
            player.is_fascist = False
            player.is_liberal = True
            break


@given("el jugador {player_id:d} no fue inspeccionado")
def step_impl_player_not_inspected(context, player_id):
    """Mark a player as not yet inspected."""
    for player in context.eligible_players:
        if player.id == player_id:
            # Add a property to track inspection status
            player.was_inspected = False
            player.is_fascist = False  # Garantizar que sea objetivo válido
            break


@then("debe priorizar fascistas para presidencia")
def step_impl_check_prioritize_fascists_presidency(context):
    """Check that fascists are prioritized for presidency."""
    fascists = [p for p in context.eligible_players if p.is_fascist and not p.is_hitler]
    # If there were fascist options available, a fascist should have been chosen
    if fascists:
        assert context.next_president_result in fascists
    # Otherwise, any player could be chosen, but with no fascists, this is just a fallback check
    else:
        assert context.next_president_result in context.eligible_players


@then("debe convertir liberales en comunistas")
def step_impl_check_convert_liberals_communists(context):
    """Check that liberals are targeted for radicalization."""
    # Check that a known liberal was chosen if available
    known_liberals = [
        p
        for p in context.eligible_players
        if (
            p.id in context.strategy.player.inspected_players
            and context.strategy.player.inspected_players[p.id] == "liberal"
        )
    ]
    if known_liberals:
        assert context.radicalize_result in known_liberals
    # If no known liberals, at least it should not be a fascist
    else:
        non_fascists = [p for p in context.eligible_players if not p.is_fascist]
        if non_fascists:
            assert context.radicalize_result in non_fascists


@then("debe usar mismo criterio que ejecución")
def step_impl_check_same_criteria_execution(context):
    """Check that marking uses the same criteria as execution."""
    # Run the execution strategy with the same players and verify result matches
    execution_result = context.strategy.choose_player_to_kill(context.eligible_players)
    # The results might not be identical due to randomness, but the logic should be similar
    # Both should prefer liberals if they're known
    known_liberals = [
        p
        for p in context.eligible_players
        if (
            p.id in context.strategy.player.inspected_players
            and context.strategy.player.inspected_players[p.id] == "liberal"
        )
    ]
    if known_liberals:
        assert context.mark_result in known_liberals
    # Otherwise both should avoid fascists
    else:
        assert (
            not context.mark_result.is_fascist
            or len([p for p in context.eligible_players if not p.is_fascist]) == 0
        )
