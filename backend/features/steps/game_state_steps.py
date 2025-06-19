from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when
from src.game.game_state import EnhancedGameState


@given("un estado de juego nuevo")
def step_impl_new_game_state(context):
    """Initialize a new game state."""
    context.game_state = EnhancedGameState()
    # Create a mock board for compatibility with existing steps
    context.board = Mock()
    context.board.veto_available = context.game_state.veto_available
    context.board.liberal_track = context.game_state.liberal_track
    context.board.fascist_track = context.game_state.fascist_track
    context.board.communist_track = context.game_state.communist_track


@given("un estado de juego con {num_players:d} jugadores")
def step_impl_game_state_with_players(context, num_players):
    """Initialize a game state with a specific number of players."""
    context.game_state = EnhancedGameState()
    context.players = []

    # Create a mock board for compatibility with existing steps
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


@given("el jugador {player_index:d} es el candidato a presidente")
def step_impl_president_candidate(context, player_index):
    """Set a specific player as president candidate."""
    context.game_state.president_candidate = context.players[player_index]


@given("el jugador {player_index:d} es el presidente actual")
def step_impl_current_president(context, player_index):
    """Set a specific player as current president."""
    context.game_state.president = context.players[player_index]


@given("el jugador {player_index:d} está en la lista de term-limited")
def step_impl_term_limited_player(context, player_index):
    """Add a player to the term-limited list."""
    context.game_state.term_limited_players.append(context.players[player_index])


@given("el jugador {player_index:d} está muerto")
def step_impl_dead_player(context, player_index):
    """Mark a player as dead."""
    player = context.players[player_index]
    player.is_dead = True
    if player in context.game_state.active_players:
        context.game_state.active_players.remove(player)


@given("el tracker de elecciones es {count:d}")
def step_impl_election_tracker_value(context, count):
    """Set election tracker to specific value."""
    context.game_state.election_tracker = count


@given("estoy en elección especial con retorno al índice {return_index:d}")
def step_impl_special_election_with_return(context, return_index):
    """Set up special election with return index."""
    context.game_state.special_election = True
    context.game_state.special_election_return_index = return_index


@when("agrego {num_players:d} jugadores al estado de juego")
def step_impl_add_players(context, num_players):
    """Add players to game state."""
    context.players = []
    for i in range(num_players):
        player = Mock()
        player.id = i
        player.name = f"Player {i}"
        player.is_dead = False
        context.players.append(player)
        context.game_state.add_player(player)


@when("verifico los candidatos elegibles para canciller")
def step_impl_check_eligible_chancellors(context):
    """Check eligible chancellors."""
    context.eligible_chancellors = context.game_state.get_eligible_chancellors()


@when("calculo el siguiente presidente")
def step_impl_calculate_next_president(context):
    """Calculate the next president."""
    next_active_index = context.game_state.get_next_president_index()
    # Convert active player index to original player index
    next_player = context.game_state.active_players[next_active_index]
    context.next_president_index = next_player.id


@when("el jugador {player_index:d} muere")
def step_impl_player_dies(context, player_index):
    """Handle player death."""
    context.game_state.handle_player_death(context.players[player_index])


@when("incremento el tracker de elecciones")
def step_impl_increment_election_tracker(context):
    """Increment election tracker."""
    context.game_state.election_tracker += 1


@when("reseteo el tracker de elecciones")
def step_impl_reset_election_tracker(context):
    """Reset election tracker."""
    context.game_state.reset_election_tracker()


@when("incremento la pista liberal")
def step_impl_increment_liberal_track(context):
    """Increment liberal track."""
    context.game_state.liberal_track += 1
    # Sync with mock board for compatibility
    context.board.liberal_track = context.game_state.liberal_track


@when("incremento la pista fascista {count:d} veces")
def step_impl_increment_fascist_track_multiple(context, count):
    """Increment fascist track multiple times."""
    for _ in range(count):
        context.game_state.fascist_track += 1
    # Sync with mock board for compatibility
    context.board.fascist_track = context.game_state.fascist_track


@when("incremento la pista comunista")
def step_impl_increment_communist_track(context):
    """Increment communist track."""
    context.game_state.communist_track += 1
    # Sync with mock board for compatibility
    context.board.communist_track = context.game_state.communist_track


@when("establezco el veto como disponible")
def step_impl_set_veto_available(context):
    """Set veto as available."""
    context.game_state.veto_available = True
    # Sync with mock board for compatibility
    context.board.veto_available = context.game_state.veto_available


@when("investigo al jugador {player_index:d}")
def step_impl_investigate_player(context, player_index):
    """Investigate a player."""
    player = context.players[player_index]
    context.game_state.investigated_players.append(player)


@when("marco al jugador {player_index:d} para ejecución")
def step_impl_mark_for_execution(context, player_index):
    """Mark a player for execution."""
    player = context.players[player_index]
    context.game_state.marked_for_execution.append(player)


@when("inicio una elección especial con retorno al índice {return_index:d}")
def step_impl_start_special_election(context, return_index):
    """Start a special election."""
    context.game_state.special_election = True
    context.game_state.special_election_return_index = return_index


@when("revelo que el jugador {player_index:d} es {affiliation}")
def step_impl_reveal_affiliation(context, player_index, affiliation):
    """Reveal a player's affiliation."""
    player = context.players[player_index]
    context.game_state.revealed_affiliations[player.id] = affiliation


@when("incremento la pista fascista")
def step_impl_increment_fascist_track_once(context):
    """Increment fascist track once."""
    context.game_state.fascist_track += 1
    # Sync with mock board for compatibility
    context.board.fascist_track = context.game_state.fascist_track


# Removed conflicting step - using existing step from board_steps.py


@then("el tracker de elecciones debe ser {expected:d}")
def step_impl_election_tracker_value_check(context, expected):
    """Check election tracker value."""
    assert context.game_state.election_tracker == expected


@then("la lista de jugadores debe estar vacía")
def step_impl_empty_players_list(context):
    """Assert players list is empty."""
    assert len(context.game_state.players) == 0


@then("debe haber {expected:d} jugadores en total")
def step_impl_total_players_count(context, expected):
    """Check total players count."""
    assert len(context.game_state.players) == expected


@then("debe haber {expected:d} jugadores activos")
def step_impl_active_players_count(context, expected):
    """Check active players count."""
    assert len(context.game_state.active_players) == expected


@then("todos los jugadores deben estar vivos")
def step_impl_all_players_alive(context):
    """Assert all players are alive."""
    for player in context.game_state.players:
        assert not player.is_dead


@then("deben haber {expected:d} candidatos elegibles")
def step_impl_eligible_chancellors_count(context, expected):
    """Check number of eligible chancellors."""
    assert len(context.eligible_chancellors) == expected


@then("el jugador {player_index:d} no debe ser elegible")
def step_impl_player_not_eligible(context, player_index):
    """Assert player is not eligible."""
    player = context.players[player_index]
    assert player not in context.eligible_chancellors


@then("el siguiente presidente debe ser el jugador {expected_index:d}")
def step_impl_next_president_check(context, expected_index):
    """Check next president index."""
    assert context.next_president_index == expected_index


@then("el jugador {player_index:d} debe estar muerto")
def step_impl_player_is_dead(context, player_index):
    """Assert player is dead."""
    assert context.players[player_index].is_dead


@then("el siguiente candidato a presidente debe ser establecido")
def step_impl_president_candidate_set(context):
    """Assert president candidate is set."""
    assert context.game_state.president_candidate is not None


# Removed conflicting step - using existing step from board_steps.py


@then("el jugador {player_index:d} debe estar en la lista de investigados")
def step_impl_player_in_investigated_list(context, player_index):
    """Assert player is in investigated list."""
    player = context.players[player_index]
    assert player in context.game_state.investigated_players


@then("la lista de investigados debe tener {expected:d} jugador")
@then("la lista de investigados debe tener {expected:d} jugadores")
def step_impl_investigated_list_count(context, expected):
    """Check investigated players count."""
    assert len(context.game_state.investigated_players) == expected


@then("el jugador {player_index:d} debe estar marcado para ejecución")
def step_impl_player_marked_for_execution(context, player_index):
    """Assert player is marked for execution."""
    player = context.players[player_index]
    assert player in context.game_state.marked_for_execution


@then("la lista de marcados para ejecución debe tener {expected:d} jugador")
@then("la lista de marcados para ejecución debe tener {expected:d} jugadores")
def step_impl_marked_for_execution_count(context, expected):
    """Check marked for execution count."""
    assert len(context.game_state.marked_for_execution) == expected


@then("debe estar en elección especial")
def step_impl_in_special_election(context):
    """Assert in special election."""
    assert context.game_state.special_election


@then("el índice de retorno debe ser {expected:d}")
def step_impl_return_index_check(context, expected):
    """Check special election return index."""
    assert context.game_state.special_election_return_index == expected


@then("no debe estar en elección especial")
def step_impl_not_in_special_election(context):
    """Assert not in special election."""
    assert not context.game_state.special_election


@then("la afiliación del jugador {player_index:d} debe ser {expected_affiliation}")
def step_impl_player_affiliation_check(context, player_index, expected_affiliation):
    """Check player's revealed affiliation."""
    player = context.players[player_index]
    assert context.game_state.revealed_affiliations[player.id] == expected_affiliation


@then("la pista fascista debe tener {expected:d} políticas")
def step_impl_fascist_track_count(context, expected):
    """Check fascist track count."""
    assert context.game_state.fascist_track == expected


@then("la pista comunista debe tener {expected:d} políticas")
def step_impl_communist_track_count(context, expected):
    """Check communist track count."""
    assert context.game_state.communist_track == expected
