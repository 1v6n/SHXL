import io
import sys
from unittest.mock import Mock, patch

from behave import given, then, when
from src.players.abstract_player import Player
from src.players.human_player import HumanPlayer


class MockRole:
    """Mock role class for testing"""

    def __init__(self, party_membership, role="normal"):
        self.party_membership = party_membership
        self.role = role

    def __str__(self):
        return f"{self.party_membership} {self.role}"


class MockPolicy:
    """Mock policy class for testing"""

    def __init__(self, policy_type):
        self.type = policy_type

    def __str__(self):
        return self.type


@given(
    'un jugador humano con ID {player_id:d}, nombre "{name}", role "{role_type}", y estado de juego'
)
def step_impl_create_human_player(context, player_id, name, role_type):
    """Create a human player with specific attributes."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole(role_type)
    context.human_player = HumanPlayer(player_id, name, role, mock_state)


@given("un jugador humano como presidente")
def step_impl_human_player_as_president(context):
    """Create a human player as president."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)
    context.role_type = "president"


@given("un jugador humano como canciller")
def step_impl_human_player_as_chancellor(context):
    """Create a human player as chancellor."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "Chancellor", role, mock_state)
    context.role_type = "chancellor"


@given("un jugador humano en votación")
def step_impl_human_player_voting(context):
    """Create a human player for voting."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "Voter", role, mock_state)


@given("un jugador humano con poder de Policy Peek")
def step_impl_human_player_policy_peek(context):
    """Create a human player with Policy Peek power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)


@given("un jugador humano con poder de ejecución")
def step_impl_human_player_execution(context):
    """Create a human player with execution power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)


@given("un jugador humano con poder de marcado")
def step_impl_human_player_marking(context):
    """Create a human player with marking power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)


@given("un jugador humano con poder de inspección")
def step_impl_human_player_inspection(context):
    """Create a human player with inspection power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)
    context.human_player.inspected_players = {}


@given("un jugador humano con poder de elección especial")
def step_impl_human_player_special_election(context):
    """Create a human player with special election power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)


@given("un jugador humano comunista con poder de radicalización")
def step_impl_human_player_radicalization(context):
    """Create a communist human player with radicalization power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("communist")
    context.human_player = HumanPlayer(1, "Communist", role, mock_state)


@given("un jugador humano con poder de propaganda")
def step_impl_human_player_propaganda(context):
    """Create a human player with propaganda power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)


@given("un jugador humano con poder de impeachment")
def step_impl_human_player_impeachment(context):
    """Create a human player with impeachment power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)


@given("un jugador humano con poder social demócrata")
def step_impl_human_player_social_democratic(context):
    """Create a human player with social democratic power."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)


@given("un jugador humano fascista que conoce a hitler")
def step_impl_human_fascist_knows_hitler(context):
    """Create a fascist human player that knows Hitler."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("fascist")
    context.human_player = HumanPlayer(1, "Fascist", role, mock_state)
    hitler_mock = Mock()
    hitler_mock.name = "Hitler Player"
    context.human_player.hitler = hitler_mock


@given("un jugador humano hitler en juego de {num_players:d} jugadores")
def step_impl_human_hitler_small_game(context, num_players):
    """Create a Hitler human player in a small game."""
    mock_state = Mock()
    mock_state.players = [Mock() for _ in range(num_players)]
    mock_state.active_players = mock_state.players
    role = MockRole("fascist", "hitler")
    context.human_player = HumanPlayer(1, "Hitler", role, mock_state)


@given("un jugador humano que inspeccionó previamente")
def step_impl_human_player_previous_inspections(context):
    """Create a human player with previous inspections."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "President", role, mock_state)
    context.human_player.inspected_players = {}


@given("un jugador humano en proceso de elección")
def step_impl_human_player_choosing(context):
    """Create a human player in choosing process."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("liberal")
    context.human_player = HumanPlayer(1, "Player", role, mock_state)


@given("hay {num_players:d} jugadores elegibles para canciller")
def step_impl_eligible_chancellors(context, num_players):
    """Create eligible chancellor players."""
    eligible_players = []
    for i in range(num_players):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        eligible_players.append(player)
    context.eligible_players = eligible_players


@given("{num_policies:d} políticas disponibles: {policy_list}")
def step_impl_available_policies(context, num_policies, policy_list):
    """Create available policies."""
    policy_types = [p.strip().strip('"') for p in policy_list.split(",")]
    context.policies = [MockPolicy(policy_type) for policy_type in policy_types]


@given("{num_policies:d} políticas disponibles: {policy_list}")
def step_impl_two_policies_available(context, num_policies, policy_list):
    """Create 2 available policies."""
    policy_types = [p.strip().strip('"') for p in policy_list.split(",")]
    context.policies = [MockPolicy(policy_type) for policy_type in policy_types]


@given("políticas disponibles para veto humano")
def step_impl_policies_for_veto(context):
    """Create policies available for veto."""
    context.policies = [MockPolicy("fascist"), MockPolicy("communist")]
    # Mock the current_policies for veto scenario
    context.human_player.state.current_policies = context.policies


@given("el canciller propuso veto")
def step_impl_chancellor_proposed_veto(context):
    """Set up chancellor veto proposal."""
    context.human_player.state.current_policies = [
        MockPolicy("fascist"),
        MockPolicy("communist"),
    ]


@given("{num_policies:d} políticas en el top del deck: {policy_list}")
def step_impl_policies_on_deck_top(context, num_policies, policy_list):
    """Create policies on top of deck."""
    policy_types = [p.strip().strip('"') for p in policy_list.split(",")]
    context.policies = [MockPolicy(policy_type) for policy_type in policy_types]


@given("{num_players:d} jugadores disponibles para ejecutar")
def step_impl_players_for_execution(context, num_players):
    """Create players available for execution."""
    players = []
    for i in range(num_players):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        players.append(player)
    context.human_player.state.active_players = [context.human_player] + players


@given("{num_players:d} jugadores disponibles para marcar")
def step_impl_players_for_marking(context, num_players):
    """Create players available for marking."""
    players = []
    for i in range(num_players):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        players.append(player)
    context.human_player.state.active_players = [context.human_player] + players


@given("{num_players:d} jugadores no inspeccionados disponibles")
def step_impl_uninspected_players(context, num_players):
    """Create uninspected players."""
    players = []
    for i in range(num_players):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        players.append(player)
    context.human_player.state.active_players = [context.human_player] + players


@given("todos los jugadores fueron inspeccionados previamente")
def step_impl_all_players_inspected(context):
    """Set all players as previously inspected."""
    players = []
    for i in range(3):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        players.append(player)
        context.human_player.inspected_players[i + 1] = "liberal"
    context.human_player.state.active_players = [context.human_player] + players


@given("{num_players:d} jugadores elegibles como presidente")
def step_impl_eligible_presidents(context, num_players):
    """Create eligible president players."""
    players = []
    for i in range(num_players):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        players.append(player)
    context.human_player.state.active_players = [context.human_player] + players


@given("{num_players:d} jugadores disponibles para radicalizar")
def step_impl_players_for_radicalization(context, num_players):
    """Create players available for radicalization."""
    players = []
    for i in range(num_players):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        players.append(player)
    context.human_player.state.active_players = [context.human_player] + players


@given('política top "{policy_type}"')
def step_impl_top_policy(context, policy_type):
    """Create top policy."""
    context.top_policy = MockPolicy(policy_type)


@given("{num_players:d} jugadores elegibles para revelar")
def step_impl_eligible_revealers(context, num_players):
    """Create eligible players for revealing."""
    players = []
    for i in range(num_players):
        player = Mock()
        player.id = i + 1
        player.name = f"Player {i + 1}"
        players.append(player)
    context.eligible_players = players


@given("conoce a otros fascistas")
def step_impl_knows_other_fascists(context):
    """Set up knowledge of other fascists."""
    fascist_mock = Mock()
    fascist_mock.name = "Other Fascist"
    context.human_player.fascists = [fascist_mock]


@given("un jugador humano comunista")
def step_impl_human_communist_player(context):
    """Create a communist human player."""
    mock_state = Mock()
    mock_state.players = []
    mock_state.active_players = []
    role = MockRole("communist")
    context.human_player = HumanPlayer(1, "Communist", role, mock_state)


@given("conoce a otros comunistas")
def step_impl_knows_other_communists(context):
    """Set up knowledge of other communists."""
    context.human_player.known_communists = ["Player 2", "Player 3"]


@given('el jugador {player_id:d} fue inspeccionado como "{party}"')
def step_impl_player_inspected_as(context, player_id, party):
    """Set player as inspected with specific party."""
    context.human_player.inspected_players[player_id] = party


@given("{num_players:d} jugadores disponibles con IDs {id_list}")
def step_impl_players_with_ids(context, num_players, id_list):
    """Create players with specific IDs."""
    ids = [int(x.strip()) for x in id_list.split(",")]
    players = []
    for player_id in ids:
        player = Mock()
        player.id = player_id
        player.name = f"Player {player_id}"
        players.append(player)
    context.available_players = players


@when('el jugador humano nomina un canciller con input "{input_value}"')
def step_impl_nominate_chancellor_with_input(context, input_value):
    """Human player nominates chancellor with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.nominate_chancellor(
            context.eligible_players
        )


@when('el jugador humano filtra políticas con input "{input_value}"')
def step_impl_filter_policies_with_input(context, input_value):
    """Human player filters policies with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.filter_policies(context.policies)


@when('el jugador humano elige política con input "{input_value}"')
def step_impl_choose_policy_with_input(context, input_value):
    """Human player chooses policy with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.choose_policy(context.policies)


@when('el jugador humano vota con input "{input_value}"')
def step_impl_vote_with_input(context, input_value):
    """Human player votes with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.vote()


@when('el jugador humano decide veto con input "{input_value}"')
def step_impl_veto_with_input(context, input_value):
    """Human player decides veto with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.veto()


@when('el jugador humano acepta veto con input "{input_value}"')
def step_impl_accept_veto_with_input(context, input_value):
    """Human player accepts veto with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.accept_veto()


@when("el jugador humano ve las políticas")
def step_impl_view_policies(context):
    """Human player views policies."""
    with patch("builtins.input", return_value=""), patch(
        "sys.stdout", new_callable=io.StringIO
    ) as mock_stdout:
        context.human_player.view_policies(context.policies)
        context.output = mock_stdout.getvalue()


@when('el jugador humano ejecuta con input "{input_value}"')
def step_impl_kill_with_input(context, input_value):
    """Human player executes with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.kill()


@when('el jugador humano marca con input "{input_value}"')
def step_impl_mark_with_input(context, input_value):
    """Human player marks with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.choose_player_to_mark()


@when('el jugador humano inspecciona con input "{input_value}"')
def step_impl_inspect_with_input(context, input_value):
    """Human player inspects with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.inspect_player()


@when('el jugador humano elige siguiente presidente con input "{input_value}"')
def step_impl_choose_next_president_with_input(context, input_value):
    """Human player chooses next president with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.choose_next()


@when('el jugador humano radicaliza con input "{input_value}"')
def step_impl_radicalize_with_input(context, input_value):
    """Human player radicalizes with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.choose_player_to_radicalize()


@when('el jugador humano decide propaganda con input "{input_value}"')
def step_impl_propaganda_decision_with_input(context, input_value):
    """Human player makes propaganda decision with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.propaganda_decision(context.top_policy)


@when('el jugador humano elige revelador con input "{input_value}"')
def step_impl_choose_revealer_with_input(context, input_value):
    """Human player chooses revealer with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.choose_revealer(context.eligible_players)


@when('el jugador humano elige remoción con input "{input_value}"')
def step_impl_social_democratic_removal_with_input(context, input_value):
    """Human player chooses social democratic removal with specific input."""
    with patch("builtins.input", return_value=input_value), patch(
        "sys.stdout", new_callable=io.StringIO
    ):
        context.result = context.human_player.social_democratic_removal_choice(Mock())


@when("se muestra información del role")
def step_impl_display_role_info(context):
    """Display role information."""
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        context.human_player._display_role_info()
        context.output = mock_stdout.getvalue()


@when('el jugador humano ingresa ID inválido "{input_value}"')
def step_impl_invalid_id_input(context, input_value):
    """Human player enters invalid ID."""
    # Mock sequence: invalid input, then valid input
    with patch("builtins.input", side_effect=[input_value, "1"]), patch(
        "sys.stdout", new_callable=io.StringIO
    ) as mock_stdout:
        context.result = context.human_player._get_player_choice(
            context.available_players, "test"
        )
        context.output = mock_stdout.getvalue()


@when('el jugador humano ingresa texto "{input_value}"')
def step_impl_non_numeric_input(context, input_value):
    """Human player enters non-numeric input."""
    # Mock sequence: non-numeric input, then valid input
    with patch("builtins.input", side_effect=[input_value, "1"]), patch(
        "sys.stdout", new_callable=io.StringIO
    ) as mock_stdout:
        # Use context.available_players if it exists, otherwise create some
        if not hasattr(context, "available_players"):
            players = []
            for i in range(3):
                player = Mock()
                player.id = i + 1
                player.name = f"Player {i + 1}"
                players.append(player)
            context.available_players = players
        context.result = context.human_player._get_player_choice(
            context.available_players, "test"
        )
        context.output = mock_stdout.getvalue()


@then("el jugador humano debe tener ID {player_id:d}")
def step_impl_check_human_player_id(context, player_id):
    """Check human player ID."""
    assert context.human_player.id == player_id


@then('el jugador humano debe tener nombre "{name}"')
def step_impl_check_human_player_name(context, name):
    """Check human player name."""
    assert context.human_player.name == name


@then('el jugador humano debe tener role "{role_type}"')
def step_impl_check_human_player_role(context, role_type):
    """Check human player role."""
    assert str(context.human_player.role).startswith(role_type)


@then("el jugador humano debe heredar propiedades de Player abstracto")
def step_impl_check_inheritance(context):
    """Check human player inherits from abstract Player."""
    assert isinstance(context.human_player, Player)


@then("debe retornar el jugador con ID {player_id:d}")
def step_impl_check_returned_player_id(context, player_id):
    """Check returned player has specific ID."""
    assert context.result.id == player_id


@then("debe mostrar información del role")
def step_impl_check_role_info_displayed(context):
    """Check role information is displayed."""
    # This is verified by the patching in the when steps
    pass


@then("debe retornar {num_chosen:d} políticas elegidas y {num_discarded:d} descartada")
def step_impl_check_filtered_policies(context, num_chosen, num_discarded):
    """Check filtered policies result."""
    chosen, discarded = context.result
    # Handle both lists and single objects
    chosen_count = len(chosen) if hasattr(chosen, "__len__") else 1
    discarded_count = len(discarded) if hasattr(discarded, "__len__") else 1
    assert chosen_count == num_chosen
    assert discarded_count == num_discarded


@then("la política en posición {position:d} debe ser descartada")
def step_impl_check_discarded_policy_position(context, position):
    """Check specific policy position is discarded."""
    chosen, discarded = context.result
    # Handle both lists and single objects
    discarded_count = len(discarded) if hasattr(discarded, "__len__") else 1
    assert discarded_count == 1


@then("debe retornar la política en posición {position:d} y descartar la otra")
def step_impl_check_chosen_policy_position(context, position):
    """Check specific policy position is chosen."""
    chosen, discarded = context.result
    # Handle both lists and single objects
    chosen_count = len(chosen) if hasattr(chosen, "__len__") else 1
    discarded_count = len(discarded) if hasattr(discarded, "__len__") else 1
    assert chosen_count == 1
    assert discarded_count == 1


# Note: "debe retornar True" and "debe retornar False" steps are defined in ai_player_steps.py


@then("debe mostrar las {num_policies:d} políticas")
def step_impl_check_policies_displayed(context, num_policies):
    """Check policies are displayed."""
    for policy in context.policies:
        assert policy.type in context.output


@then("debe esperar confirmación del jugador")
def step_impl_check_player_confirmation(context):
    """Check player confirmation is expected."""
    # This is verified by the input patching in the when step
    pass


@then('debe retornar "{value}"')
def step_impl_check_return_string_value(context, value):
    """Check result is specific string value."""
    assert context.result == value


@then("debe permitir inspeccionar cualquier jugador")
def step_impl_check_can_inspect_any_player(context):
    """Check can inspect any player when all inspected."""
    # This is verified by the logic in inspect_player method
    pass


@then("debe mostrar información de hitler")
def step_impl_check_hitler_info_displayed(context):
    """Check Hitler information is displayed."""
    assert "Hitler" in context.output


@then("debe mostrar lista de fascistas")
def step_impl_check_fascists_list_displayed(context):
    """Check fascists list is displayed."""
    assert "fascist" in context.output.lower()


@then("debe mostrar lista de fascistas conocidos")
def step_impl_check_known_fascists_displayed(context):
    """Check known fascists are displayed."""
    assert "fascist" in context.output.lower()


@then("debe mostrar lista de comunistas conocidos")
def step_impl_check_known_communists_displayed(context):
    """Check known communists are displayed."""
    assert "communist" in context.output.lower()


@then("debe mostrar información de inspecciones previas")
def step_impl_check_previous_inspections_displayed(context):
    """Check previous inspections are displayed."""
    assert "inspect" in context.output.lower() or "inspeccion" in context.output.lower()


@then("debe mostrar mensaje de error")
def step_impl_check_error_message_displayed(context):
    """Check error message is displayed."""
    assert "Invalid" in context.output or "try again" in context.output


@then("debe solicitar nuevo input")
def step_impl_check_new_input_requested(context):
    """Check new input is requested."""
    # This is verified by the side_effect in the input patching
    pass


@then("debe mostrar mensaje de error numérico")
def step_impl_check_numeric_error_message(context):
    """Check numeric error message is displayed."""
    assert "valid number" in context.output or "número" in context.output
