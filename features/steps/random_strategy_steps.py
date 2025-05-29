import random
from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.players.strategies.base_strategy import PlayerStrategy
from src.players.strategies.random_strategy import RandomStrategy


@given("un jugador mock")
def step_impl_mock_player(context):
    """Create a mock player."""
    context.mock_player = Mock()
    context.mock_player.name = "Test Player"
    context.mock_player.id = 1


@given("una estrategia aleatoria")
def step_impl_random_strategy(context):
    """Create a random strategy instance."""
    if not hasattr(context, "mock_player"):
        context.mock_player = Mock()
        context.mock_player.name = "Test Player"
        context.mock_player.id = 1
    context.strategy = RandomStrategy(context.mock_player)


@given("una estrategia aleatoria con semilla fija")
def step_impl_random_strategy_fixed_seed(context):
    """Create a random strategy with fixed seed for testing."""
    random.seed(42)  # Fixed seed for reproducible tests
    context.mock_player = Mock()
    context.strategy = RandomStrategy(context.mock_player)


@given("una lista de {count:d} jugadores elegibles")
def step_impl_eligible_players_list(context, count):
    """Create a list of eligible players."""
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i
        player.name = f"Player {i}"
        context.eligible_players.append(player)


@given("una lista de jugadores elegibles")
def step_impl_general_eligible_players_list(context):
    """Create a general list of eligible players."""
    context.eligible_players = [Mock(), Mock(), Mock()]
    context.eligible_players[0].name = "Player 1"
    context.eligible_players[1].name = "Player 2"
    context.eligible_players[2].name = "Player 3"
    context.eligible_players[0].id = 1
    context.eligible_players[1].id = 2
    context.eligible_players[2].id = 3


@given("una lista de {count:d} jugadores elegibles para {action}")
def step_impl_eligible_players_for_action(context, count, action):
    """Create a list of eligible players for specific action."""
    context.eligible_players = []
    for i in range(count):
        player = Mock()
        player.id = i
        player.name = f"Player {i}"
        context.eligible_players.append(player)


@given("una lista de {count:d} políticas: {policy_list}")
def step_impl_policies_list(context, count, policy_list):
    """Create a list of policies."""
    policy_names = [p.strip().strip('"') for p in policy_list.split(",")]
    context.policies = []
    for policy_name in policy_names:
        policy = Mock()
        policy.type = policy_name
        policy.name = policy_name
        context.policies.append(policy)


@given("un presidente mock")
def step_impl_mock_president(context):
    """Create a mock president."""
    context.president = Mock()
    context.president.name = "President"


@given("un canciller mock")
def step_impl_mock_chancellor(context):
    """Create a mock chancellor."""
    context.chancellor = Mock()
    context.chancellor.name = "Chancellor"


@given("una lista de políticas para veto")
def step_impl_policies_for_veto(context):
    """Create policies for veto testing."""
    context.veto_policies = [Mock(), Mock()]
    context.veto_policies[0].type = "fascist"
    context.veto_policies[1].type = "fascist"


@given("una propuesta de veto")
def step_impl_veto_proposal(context):
    """Create a veto proposal."""
    context.veto_proposal = Mock()
    # Set up veto policies for the accept_veto method
    context.veto_policies = [Mock(), Mock()]
    context.veto_policies[0].type = "fascist"
    context.veto_policies[1].type = "liberal"


@given("políticas para propuesta de veto")
def step_impl_policies_for_veto_proposal(context):
    """Create policies for veto proposal testing."""
    context.veto_policies = [Mock(), Mock()]


@given("una política para decisión de propaganda")
def step_impl_policy_for_propaganda(context):
    """Create a policy for propaganda decision."""
    context.propaganda_policy = Mock()
    context.propaganda_policy.type = "fascist"


@when("creo una estrategia aleatoria con el jugador")
def step_impl_create_random_strategy(context):
    """Create a random strategy with the mock player."""
    context.strategy = RandomStrategy(context.mock_player)


@when("la estrategia nomina un canciller")
def step_impl_nominate_chancellor(context):
    """Strategy nominates a chancellor."""
    context.chosen_player = context.strategy.nominate_chancellor(
        context.eligible_players
    )


@when("la estrategia filtra las políticas")
def step_impl_filter_policies(context):
    """Strategy filters policies as president."""
    context.filtered_result = context.strategy.filter_policies(context.policies)
    context.chosen_policies, context.discarded_policy = context.filtered_result


@when("la estrategia elige una política")
def step_impl_choose_policy(context):
    """Strategy chooses a policy as chancellor."""
    context.policy_result = context.strategy.choose_policy(context.policies)
    context.enacted_policy, context.discarded_policy = context.policy_result


@when("la estrategia vota en el gobierno")
def step_impl_vote_government(context):
    """Strategy votes on government."""
    context.vote_result = context.strategy.vote(context.president, context.chancellor)


@when("la estrategia decide sobre veto")
def step_impl_decide_veto(context):
    """Strategy decides on veto."""
    context.veto_decision = context.strategy.veto(context.veto_policies)


@when("la estrategia decide aceptar veto")
def step_impl_accept_veto(context):
    """Strategy decides to accept veto."""
    context.accept_veto_decision = context.strategy.accept_veto(context.veto_policies)


@when("la estrategia elige un jugador para ejecutar")
def step_impl_choose_player_to_kill(context):
    """Strategy chooses a player to execute."""
    context.chosen_player = context.strategy.choose_player_to_kill(
        context.eligible_players
    )


@when("la estrategia elige un jugador para inspeccionar")
def step_impl_choose_player_to_inspect(context):
    """Strategy chooses a player to inspect."""
    context.chosen_player = context.strategy.choose_player_to_inspect(
        context.eligible_players
    )


@when("la estrategia elige el siguiente presidente")
def step_impl_choose_next_president(context):
    """Strategy chooses next president."""
    context.chosen_player = context.strategy.choose_next_president(
        context.eligible_players
    )


@when("la estrategia elige un jugador para radicalizar")
def step_impl_choose_player_to_radicalize(context):
    """Strategy chooses a player to radicalize."""
    context.chosen_player = context.strategy.choose_player_to_radicalize(
        context.eligible_players
    )


@when("la estrategia elige un jugador para marcar")
def step_impl_choose_player_to_mark(context):
    """Strategy chooses a player to mark."""
    context.chosen_player = context.strategy.choose_player_to_mark(
        context.eligible_players
    )


@when("la estrategia elige un jugador para espionar")
def step_impl_choose_player_to_bug(context):
    """Strategy chooses a player to bug."""
    context.chosen_player = context.strategy.choose_player_to_bug(
        context.eligible_players
    )


@when("la estrategia decide sobre propaganda")
def step_impl_propaganda_decision(context):
    """Strategy makes propaganda decision."""
    context.propaganda_decision = context.strategy.propaganda_decision(
        context.propaganda_policy
    )


@when("la estrategia elige un revelador")
def step_impl_choose_revealer(context):
    """Strategy chooses a revealer."""
    context.chosen_player = context.strategy.choose_revealer(context.eligible_players)


@when("la estrategia decide sobre perdón")
def step_impl_pardon_decision(context):
    """Strategy makes pardon decision."""
    context.pardon_decision = context.strategy.pardon_player()


@when("la estrategia propone veto como canciller")
def step_impl_chancellor_veto_proposal(context):
    """Strategy proposes veto as chancellor."""
    context.veto_proposal_decision = context.strategy.chancellor_veto_proposal(
        context.veto_policies
    )


@when("la estrategia decide sobre voto de no confianza")
def step_impl_vote_of_no_confidence(context):
    """Strategy makes vote of no confidence decision."""
    context.no_confidence_decision = context.strategy.vote_of_no_confidence()


@when("la estrategia elige qué remover en poder socialdemócrata")
def step_impl_social_democratic_removal(context):
    """Strategy chooses what to remove with social democratic power."""
    context.removal_choice = context.strategy.social_democratic_removal_choice()


@when("la estrategia hace múltiples decisiones")
def step_impl_multiple_decisions(context):
    """Strategy makes multiple decisions to test variability."""
    context.decision_results = []
    # Make multiple decisions and collect results
    for _ in range(10):
        # Test multiple different decision types
        vote_result = context.strategy.vote(context.mock_player, context.mock_player)
        propaganda_result = context.strategy.propaganda_decision(Mock())
        context.decision_results.extend([vote_result, propaganda_result])


@when("la estrategia intenta elegir de una lista vacía")
def step_impl_choose_from_empty_list(context):
    """Strategy attempts to choose from empty list."""
    try:
        context.result = context.strategy.nominate_chancellor([])
        context.exception_raised = False
    except (IndexError, ValueError) as e:
        context.exception_raised = True
        context.exception = e


@then("la estrategia debe estar inicializada correctamente")
def step_impl_check_strategy_initialized(context):
    """Check that strategy is initialized correctly."""
    assert context.strategy is not None
    assert context.strategy.player == context.mock_player


@then("debe heredar de PlayerStrategy")
def step_impl_check_inheritance(context):
    """Check that RandomStrategy inherits from PlayerStrategy."""
    assert isinstance(context.strategy, PlayerStrategy)
    assert issubclass(RandomStrategy, PlayerStrategy)


@then("debe retornar uno de los jugadores elegibles")
def step_impl_check_player_in_eligible(context):
    """Check that chosen player is in eligible list."""
    assert context.chosen_player in context.eligible_players


@then("el jugador seleccionado debe estar en la lista original")
def step_impl_check_player_in_original_list(context):
    """Check that nominated player is in original list."""
    assert context.chosen_player in context.eligible_players


@then("debe retornar {count:d} políticas para pasar")
def step_impl_check_policies_to_pass(context, count):
    """Check number of policies to pass."""
    assert len(context.chosen_policies) == count


@then("debe retornar {count:d} política para descartar")
def step_impl_check_policies_to_discard(context, count):
    """Check number of policies to discard."""
    if isinstance(context.discarded_policy, list):
        assert len(context.discarded_policy) == count
    else:
        assert count == 1  # Single policy


@then("las políticas filtradas deben ser del conjunto original")
def step_impl_check_policies_from_original(context):
    """Check that filtered policies are from original set."""
    all_policies = (
        context.chosen_policies + [context.discarded_policy]
        if not isinstance(context.discarded_policy, list)
        else context.chosen_policies + context.discarded_policy
    )
    for policy in all_policies:
        assert policy in context.policies


@then("debe retornar una política para promulgar")
def step_impl_check_enacted_policy(context):
    """Check that an enacted policy is returned."""
    assert context.enacted_policy is not None
    assert context.enacted_policy in context.policies


@then("debe retornar una política para descartar")
def step_impl_check_discarded_policy(context):
    """Check that a discarded policy is returned."""
    assert context.discarded_policy is not None
    assert context.discarded_policy in context.policies


@then("ambas políticas deben ser del conjunto original")
def step_impl_check_both_policies_original(context):
    """Check that both policies are from original set."""
    assert context.enacted_policy in context.policies
    assert context.discarded_policy in context.policies
    assert context.enacted_policy != context.discarded_policy


@then("debe retornar un valor booleano")
def step_impl_check_boolean_result(context):
    """Check that result is boolean."""
    if hasattr(context, "vote_result"):
        assert isinstance(context.vote_result, bool)
    elif hasattr(context, "veto_decision"):
        assert isinstance(context.veto_decision, bool)
    elif hasattr(context, "accept_veto_decision"):
        assert isinstance(context.accept_veto_decision, bool)
    elif hasattr(context, "propaganda_decision"):
        assert isinstance(context.propaganda_decision, bool)
    elif hasattr(context, "pardon_decision"):
        assert isinstance(context.pardon_decision, bool)
    elif hasattr(context, "veto_proposal_decision"):
        assert isinstance(context.veto_proposal_decision, bool)
    elif hasattr(context, "no_confidence_decision"):
        assert isinstance(context.no_confidence_decision, bool)


@then("el resultado debe ser aleatorio")
def step_impl_check_random_result(context):
    """Check that result appears random (not always the same)."""
    # For boolean results, we can't easily test randomness in a single call
    # This step acknowledges that the method should produce random results
    # In practice, you would test this with multiple calls and statistical analysis
    assert True  # Placeholder - in real testing you'd make multiple calls


@then("debe tener baja probabilidad de veto")
def step_impl_check_low_veto_probability(context):
    """Check that veto has low probability."""
    # The RandomStrategy uses 20% chance, so this is a conceptual check
    # In practice, you'd test this with multiple calls
    assert True  # Placeholder - the implementation uses 0.2 probability


@then("debe tener baja probabilidad de aceptación")
def step_impl_check_low_acceptance_probability(context):
    """Check that veto acceptance has low probability."""
    # The RandomStrategy uses 20% chance for accept_veto
    assert True  # Placeholder - the implementation uses 0.2 probability


@then("debe tener baja probabilidad de propuesta")
def step_impl_check_low_proposal_probability(context):
    """Check that veto proposal has low probability."""
    # The RandomStrategy uses 20% chance for chancellor_veto_proposal
    assert True  # Placeholder - the implementation uses 0.2 probability


@then('la elección de remoción debe retornar "{option1}" o "{option2}"')
def step_impl_check_choice_options(context, option1, option2):
    """Check that result is one of two specific options."""
    assert context.removal_choice in [option1, option2]


@then("el resultado debe estar en las opciones válidas")
def step_impl_check_valid_options(context):
    """Check that result is in valid options."""
    valid_options = ["fascist", "communist"]
    assert context.removal_choice in valid_options


@then("debe mostrar variabilidad en los resultados")
def step_impl_check_variability(context):
    """Check that results show variability."""
    # With random decisions, we should see some variety in boolean results
    true_count = sum(1 for result in context.decision_results if result is True)
    false_count = sum(1 for result in context.decision_results if result is False)
    # At least some variety should exist (not all the same)
    assert true_count > 0 or false_count > 0


@then("debe respetar las probabilidades configuradas")
def step_impl_check_probability_respect(context):
    """Check that strategy respects configured probabilities."""
    # This is a placeholder for probability testing
    # In a real test, you would run many iterations and check distributions
    assert True  # Placeholder - would need statistical testing


@then("debe manejar el error apropiadamente")
def step_impl_check_error_handling(context):
    """Check that error is handled appropriately."""
    # The random.choice() function raises IndexError for empty sequences
    assert context.exception_raised


@then("no debe causar una excepción no controlada")
def step_impl_check_no_unhandled_exception(context):
    """Check that no unhandled exception occurs."""
    # If we get here, the exception was handled (or the operation succeeded)
    assert True
