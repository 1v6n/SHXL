from unittest.mock import Mock

from behave import given, then, when

from src.game.game_state import EnhancedGameState
from src.players.abstract_player import Player


class MockRole:
    """Mock role class for testing"""

    def __init__(self, party_membership, role="normal"):
        self.party_membership = party_membership
        self.role = role

    def __str__(self):
        return f"{self.party_membership} {self.role}"


class TestablePlayer(Player):
    """Concrete implementation of Player for testing abstract methods"""

    def nominate_chancellor(self):
        return Mock()

    def filter_policies(self, policies):
        return (policies[:2], policies[2:])

    def choose_policy(self, policies):
        return (policies[0], policies[1])

    def vote(self):
        return True

    def veto(self):
        return False

    def accept_veto(self):
        return False

    def view_policies(self, policies):
        pass

    def kill(self):
        return Mock()

    def choose_player_to_mark(self):
        return Mock()

    def inspect_player(self):
        return Mock()

    def choose_next(self):
        return Mock()

    def choose_player_to_radicalize(self):
        return Mock()

    def propaganda_decision(self, policy):
        return False

    def choose_revealer(self, eligible_players):
        return Mock()

    def social_democratic_removal_choice(self, state):
        return "fascist"


@given(
    'un jugador abstracto con ID {player_id:d}, nombre "{name}", role "{role_type}", y estado de juego'
)
def step_impl_create_abstract_player(context, player_id, name, role_type):
    """Create an abstract player with specific attributes."""
    mock_state = Mock()
    mock_state.players = []
    role = MockRole(role_type)
    context.player = TestablePlayer(player_id, name, role, mock_state)


@given('un jugador con party membership "{party}"')
def step_impl_player_with_party(context, party):
    """Create a player with specific party membership."""
    mock_state = Mock()
    mock_state.players = []
    role = MockRole(party)
    context.player = TestablePlayer(1, "Test Player", role, mock_state)


@given('un jugador con role "{role_name}" y party membership "{party}"')
def step_impl_player_with_role_and_party(context, role_name, party):
    """Create a player with specific role and party."""
    mock_state = Mock()
    mock_state.players = []
    role = MockRole(party, role_name)
    context.player = TestablePlayer(1, "Test Player", role, mock_state)


@given("un estado de juego con {num_players:d} jugadores")
def step_impl_create_game_state_for_player(context, num_players):
    """Create a game state with specific number of players."""
    context.game_state = EnhancedGameState()
    context.players = []

    context.board = Mock()
    context.board.veto_available = context.game_state.veto_available
    context.board.liberal_track = context.game_state.liberal_track
    context.board.fascist_track = context.game_state.fascist_track
    context.board.communist_track = context.game_state.communist_track

    for i in range(num_players):
        player = Mock()
        player.id = i
        player.name = f"Player {i}"
        player.is_dead = False
        context.players.append(player)
        context.game_state.add_player(player)


@given("un jugador fascista que no es hitler")
def step_impl_fascist_not_hitler(context):
    """Create a fascist player that is not Hitler."""
    role = MockRole("fascist", "normal")
    context.player = TestablePlayer(1, "Fascist", role, context.game_state)


@given("un jugador hitler")
def step_impl_hitler_player(context):
    """Create a Hitler player."""
    role = MockRole("fascist", "hitler")
    context.player = TestablePlayer(1, "Hitler", role, context.game_state)


@given("un jugador comunista")
def step_impl_communist_player(context):
    """Create a communist player."""
    role = MockRole("communist")
    context.player = TestablePlayer(1, "Communist", role, context.game_state)


@given("un jugador abstracto inicializado")
def step_impl_initialized_abstract_player(context):
    """Create an initialized abstract player."""
    mock_state = Mock()
    mock_state.players = []
    role = MockRole("liberal")
    context.player = TestablePlayer(1, "Test Player", role, mock_state)


@given("un jugador fascista inicializado")
def step_impl_initialized_fascist_player(context):
    """Create an initialized fascist player."""
    mock_state = Mock()
    mock_state.players = []
    role = MockRole("fascist")
    context.player = TestablePlayer(1, "Fascist", role, mock_state)


@when("se inicializan los atributos del role")
def step_impl_initialize_role_attributes(context):
    """Initialize role-specific attributes."""
    context.player.initialize_role_attributes()


@when('el jugador inspecciona al jugador {player_id:d} como "{party}"')
def step_impl_inspect_player(context, player_id, party):
    """Player inspects another player."""
    context.player.inspected_players[player_id] = party


@when('se registra que el jugador {player_id:d} tiene afiliación "{party}"')
def step_impl_register_affiliation(context, player_id, party):
    """Register a player's known affiliation."""
    context.player.known_affiliations[player_id] = party


@when("se asigna hitler como el jugador {player_id:d}")
def step_impl_assign_hitler(context, player_id):
    """Assign Hitler reference."""
    hitler_mock = Mock()
    hitler_mock.id = player_id
    context.player.hitler = hitler_mock


@when("hitler no está asignado")
def step_impl_hitler_not_assigned(context):
    """Ensure Hitler is not assigned."""
    context.player.hitler = None


@then("el jugador debe tener ID {player_id:d}")
def step_impl_check_player_id(context, player_id):
    """Check player ID."""
    assert context.player.id == player_id


@then('el jugador debe tener nombre "{name}"')
def step_impl_check_player_name(context, name):
    """Check player name."""
    assert context.player.name == name


@then('el jugador debe tener role "{role_type}"')
def step_impl_check_player_role(context, role_type):
    """Check player role."""
    assert str(context.player.role).startswith(role_type)


@then("el jugador no debe estar muerto")
def step_impl_check_not_dead(context):
    """Check player is not dead."""
    assert not context.player.is_dead


@then("el contador de jugadores conocidos debe estar inicializado")
def step_impl_check_player_count_initialized(context):
    """Check player count is initialized."""
    assert hasattr(context.player, "player_count")


@then("el jugador debe ser liberal")
def step_impl_check_is_liberal(context):
    """Check player is liberal."""
    assert context.player.is_liberal


@then("el jugador no debe ser fascista")
def step_impl_check_not_fascist(context):
    """Check player is not fascist."""
    assert not context.player.is_fascist


@then("el jugador no debe ser comunista")
def step_impl_check_not_communist(context):
    """Check player is not communist."""
    assert not context.player.is_communist


@then("el jugador no debe ser hitler")
def step_impl_check_not_hitler(context):
    """Check player is not Hitler."""
    assert not context.player.is_hitler


@then("el jugador debe ser fascista")
def step_impl_check_is_fascist(context):
    """Check player is fascist."""
    assert context.player.is_fascist


@then("el jugador no debe ser liberal")
def step_impl_check_not_liberal(context):
    """Check player is not liberal."""
    assert not context.player.is_liberal


@then("el jugador debe ser comunista")
def step_impl_check_is_communist(context):
    """Check player is communist."""
    assert context.player.is_communist


@then("el jugador debe ser hitler")
def step_impl_check_is_hitler(context):
    """Check player is Hitler."""
    assert context.player.is_hitler


@then("el jugador debe tener lista de fascistas inicializada")
def step_impl_check_fascists_initialized(context):
    """Check fascists list is initialized."""
    assert hasattr(context.player, "fascists")
    assert context.player.fascists is not None


@then("el jugador debe tener referencia a hitler inicializada")
def step_impl_check_hitler_reference_initialized(context):
    """Check Hitler reference is initialized."""
    assert hasattr(context.player, "hitler")


@then("el jugador no debe conocer a otros fascistas")
def step_impl_check_no_fascist_knowledge(context):
    """Check player doesn't know other fascists."""
    assert context.player.fascists is None or len(context.player.fascists) == 0


@then("el jugador debe tener lista de comunistas conocidos inicializada")
def step_impl_check_communists_initialized(context):
    """Check communists list is initialized."""
    assert hasattr(context.player, "known_communists")
    assert context.player.known_communists is not None


@then("el jugador no debe conocer a otros comunistas")
def step_impl_check_no_communist_knowledge(context):
    """Check player doesn't know other communists."""
    assert (
        context.player.known_communists is None
        or len(context.player.known_communists) == 0
    )


@then('el jugador debe conocer que el jugador {player_id:d} es "{party}"')
def step_impl_check_player_knowledge(context, player_id, party):
    """Check player knows another player's party."""
    if player_id in context.player.inspected_players:
        assert context.player.inspected_players[player_id] == party
    elif player_id in context.player.known_affiliations:
        assert context.player.known_affiliations[player_id] == party
    else:
        assert False, f"Player {player_id} not found in known players"


@then(
    "el diccionario de jugadores inspeccionados debe contener al jugador {player_id:d}"
)
def step_impl_check_inspected_contains(context, player_id):
    """Check inspected players contains specific player."""
    assert player_id in context.player.inspected_players


@then("el diccionario de afiliaciones conocidas debe contener al jugador {player_id:d}")
def step_impl_check_affiliations_contains(context, player_id):
    """Check known affiliations contains specific player."""
    assert player_id in context.player.known_affiliations


@then("el jugador debe conocer a hitler")
def step_impl_check_knows_hitler(context):
    """Check player knows Hitler."""
    assert context.player.hitler is not None


@then("knows_hitler debe retornar True")
def step_impl_check_knows_hitler_true(context):
    """Check knows_hitler returns True."""
    assert context.player.knows_hitler


@then("el jugador no debe conocer a hitler")
def step_impl_check_not_know_hitler(context):
    """Check player doesn't know Hitler."""
    assert context.player.hitler is None


@then("knows_hitler debe retornar False")
def step_impl_check_knows_hitler_false(context):
    """Check knows_hitler returns False."""
    assert not context.player.knows_hitler


@then("la representación string debe contener el ID, nombre y role")
def step_impl_check_string_representation(context):
    """Check string representation contains required elements."""
    player_str = str(context.player)
    assert str(context.player.id) in player_str
    assert context.player.name in player_str
    assert str(context.player.role) in player_str


@then("debe tener método abstracto {method_name}")
def step_impl_check_abstract_method(context, method_name):
    """Check player has specific abstract method."""
    assert hasattr(context.player, method_name)
    method = getattr(context.player, method_name)
    assert callable(method)
    assert hasattr(Player, method_name)
    original_method = getattr(Player, method_name)
    assert getattr(original_method, "__isabstractmethod__", False)
