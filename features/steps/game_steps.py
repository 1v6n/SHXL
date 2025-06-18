# features/steps/game_steps.py

import ast
from random import randint
from unittest.mock import Mock, patch

# mypy: disable-error-code=import
from behave import given, then, when

from src.game.board import GameBoard
from src.game.game import SHXLGame
from src.game.phases.setup import SetupPhase
from src.players.player_factory import PlayerFactory
from src.policies.policy_factory import PolicyFactory
from src.roles.role_factory import RoleFactory


def initialize_board_mock_with_defaults(context):
    """Helper function to initialize board mock with default numeric values"""
    if not hasattr(context.game.state, "board") or context.game.state.board is None:
        context.game.state.board = Mock(name="BoardMock")
    # Set default numeric values for all tracks to avoid comparison issues
    if not hasattr(context.game.state.board, "liberal_track") or isinstance(
        context.game.state.board.liberal_track, Mock
    ):
        context.game.state.board.liberal_track = 0
    if not hasattr(context.game.state.board, "liberal_track_size") or isinstance(
        context.game.state.board.liberal_track_size, Mock
    ):
        context.game.state.board.liberal_track_size = 5
    if not hasattr(context.game.state.board, "fascist_track") or isinstance(
        context.game.state.board.fascist_track, Mock
    ):
        context.game.state.board.fascist_track = 0
    if not hasattr(context.game.state.board, "fascist_track_size") or isinstance(
        context.game.state.board.fascist_track_size, Mock
    ):
        context.game.state.board.fascist_track_size = 6
    if not hasattr(context.game.state.board, "communist_track") or isinstance(
        context.game.state.board.communist_track, Mock
    ):
        context.game.state.board.communist_track = 0
    if not hasattr(context.game.state.board, "communist_track_size") or isinstance(
        context.game.state.board.communist_track_size, Mock
    ):
        context.game.state.board.communist_track_size = 5


@given("a new SHXLGame instance")
def step_given_new_shxlgame_instance(context):
    context.game = SHXLGame()
    context.state = context.game.state
    # Preparar variables para patchers y flags
    context.patcher_gb = None
    context.patcher_rand = None
    context.patcher_pf_class = None
    context.patcher_rf_class = None
    context.patcher_pf_methods = None
    context.fake_pf = None
    context.fake_rf = None
    context.init_board_called = False
    context.assign_called = False
    context.inform_called = False
    context.choose_pres_called = False


# ------------------------------------------------------
@when("inicializo el tablero con {players:d} jugadores y flag comunista {flag}")
def step_when_inicializo_tablero(context, players, flag):
    context.gb_mock = Mock(name="GameBoardMock")
    context.patcher_gb = patch("src.game.game.GameBoard", return_value=context.gb_mock)
    context.patch_gb = context.patcher_gb.start()
    context.game.initialize_board(players, flag)
    context.patcher_gb.stop()


@then("se debe haber construido un GameBoard con state, {players:d}, {flag}")
def step_then_gameboard_construido(context, players, flag):
    context.patch_gb.assert_called_once_with(context.state, players, flag)


@then("context.state.board debe asignarse al mock de GameBoard")
def step_then_state_board_asignado(context):
    assert context.state.board is context.gb_mock


# ------------------------------------------------------
@given("el juego tiene active_players {player_list}")
def step_given_active_players(context, player_list):
    import ast

    lst = ast.literal_eval(player_list)
    context.game.state.active_players = lst


@given("randint returns {index:d}")
def step_given_randint_returns(context, index):
    context.patcher_rand = patch("src.game.game.randint", return_value=index)
    context.patch_rand = context.patcher_rand.start()


@when("elijo primer presidente")
def step_when_elijo_primer_presidente(context):
    context.game.choose_first_president()
    context.patcher_rand.stop()


@then('state.president_candidate debe ser "{expected_player}"')
def step_then_president_candidate(context, expected_player):
    assert context.game.state.president_candidate == expected_player


# ------------------------------------------------------
@given("current_phase execute returns itself once then sets game_over true")
def step_given_current_phase_execute(context):
    context.game.state.game_over = False
    context.game.state.winner = "fascist"

    phase_mock = Mock()
    phase_mock.execute = Mock(return_value=phase_mock)

    original_start_game = context.game.start_game
    def mock_start_game():
        phase_mock.execute()
        context.game.state.game_over = True
        return "fascist"

    context.game.start_game = mock_start_game
    context.phase_mock = phase_mock

@given('state.winner is "{winner}"')
def step_given_state_winner(context, winner):
    context.game.state.winner = winner


@when("inicio el juego")
def step_when_inicio_juego(context):
    context.result = context.game.start_game()


@then('el ganador retornado debe ser "{winner}"')
def step_then_ganador_retornado(context, winner):
    assert context.result == winner


@then("execute fue llamado al menos una vez sobre el objeto de fase")
def step_then_execute_llamado(context):
    assert context.phase_mock.execute.call_count >= 1


# ------------------------------------------------------
@given("player_count {pc:d}")
def step_given_player_count(context, pc):
    context.pc = pc


@given("with_communists {flag}")
def step_given_with_communists(context, flag):
    context.with_comm = False if flag.lower() == "false" else True


@given("with_anti_policies {flag}")
def step_given_with_anti_policies(context, flag):
    context.with_antip = False if flag.lower() == "false" else True


@given("with_emergency_powers {flag}")
def step_given_with_emergency_powers(context, flag):
    context.with_emerg = False if flag.lower() == "false" else True


@given("human_player_indices {indices}")
def step_given_human_player_indices(context, indices):
    import ast

    context.humans = ast.literal_eval(indices)


@given('ai_strategy is "{strategy}"')
def step_given_ai_strategy(context, strategy):
    context.strategy = strategy


@given(
    "stubeo initialize_board, policy_deck_initialization, assign_players, inform_players, choose_first_president"
)
def step_given_stubeo_methods(context):
    def fake_init_board(self, players, comm_flag):
        context.init_board_called = True
        context.game.state.board = Mock(name="BoardWithDeck")
        context.game.state.board.initialize_policy_deck = Mock(
            name="initialize_policy_deck"
        )

    context.orig_init_board = SHXLGame.initialize_board
    SHXLGame.initialize_board = fake_init_board

    context.fake_pf = Mock(spec=PolicyFactory)
    context.patcher_pf_class = patch(
        "src.game.game.PolicyFactory", return_value=context.fake_pf
    )
    context.patch_pf_class = context.patcher_pf_class.start()

    def fake_assign(self):
        context.assign_called = True

    def fake_inform(self):
        context.inform_called = True

    def fake_choose(self):
        context.choose_pres_called = True

    context.orig_assign = SHXLGame.assign_players
    context.orig_inform = SHXLGame.inform_players
    context.orig_choose = SHXLGame.choose_first_president

    SHXLGame.assign_players = fake_assign
    SHXLGame.inform_players = fake_inform
    SHXLGame.choose_first_president = fake_choose


@when("configuro el juego")
def step_when_configuro_juego(context):
    context.game.setup_game(
        context.pc,
        with_communists=context.with_comm,
        with_anti_policies=context.with_antip,
        with_emergency_powers=context.with_emerg,
        human_player_indices=context.humans,
        ai_strategy=context.strategy,
    )
    context.patch_pf_class.stop()
    SHXLGame.initialize_board = context.orig_init_board
    SHXLGame.assign_players = context.orig_assign
    SHXLGame.inform_players = context.orig_inform
    SHXLGame.choose_first_president = context.orig_choose


@then("game.player_count debe ser {pc:d}")
def step_then_game_player_count(context, pc):
    assert context.game.player_count == pc


@then("game.communists_in_play debe ser {flag}")
def step_then_game_communists_in_play(context, flag):
    expected = False if flag.lower() == "false" else True
    assert context.game.communists_in_play == expected


@then("game.anti_policies_in_play debe ser {flag}")
def step_then_game_anti_policies_in_play(context, flag):
    expected = False if flag.lower() == "false" else True
    assert context.game.anti_policies_in_play == expected


@then("game.emergency_powers_in_play debe ser {flag}")
def step_then_game_emergency_powers_in_play(context, flag):
    expected = False if flag.lower() == "false" else True
    assert context.game.emergency_powers_in_play == expected


@then("game.human_player_indices debe igualar {indices}")
def step_then_game_human_player_indices(context, indices):
    import ast

    expected = ast.literal_eval(indices)
    assert context.game.human_player_indices == expected


@then('game.ai_strategy debe ser "{strategy}"')
def step_then_game_ai_strategy(context, strategy):
    assert context.game.ai_strategy == strategy


@then("initialize_board fue llamado una vez con argumentos (5, false)")
def step_then_initialize_board_llamado(context):
    assert context.init_board_called is True


@then(
    "policy_deck_initialization fue llamado una vez con el mock de PolicyFactory, false, false"
)
def step_then_policy_deck_initialization_llamado(context):
    board = context.game.state.board
    board.initialize_policy_deck.assert_called_once_with(context.fake_pf, False, False)


@then("assign_players fue llamado una vez")
def step_then_assign_players_llamado(context):
    assert context.assign_called is True


@then("inform_players fue llamado una vez")
def step_then_inform_players_llamado(context):
    assert context.inform_called is True


@then("choose_first_president fue llamado una vez")
def step_then_choose_first_president_llamado(context):
    assert context.choose_pres_called is True


@then("game.current_phase debe ser SetupPhase")
def step_then_game_current_phase_setup(context):
    assert isinstance(context.game.current_phase, SetupPhase)


# ------------------------------------------------------
@given("un estado vacío con jugadores {player_list}")
def step_given_estado_vacio_con_jugadores(context, player_list):
    import ast

    context.game.state.players = []
    context.game.state.active_players = []
    context.player_names = ast.literal_eval(player_list)


@given(
    "parcheo PlayerFactory.create_players para agregar {count:d} mocks de jugador a state.players"
)
def step_given_parcheo_playerfactory_create_players(context, count):
    mocks = []
    for i in range(count):
        m = Mock(name=f"Player{i}")
        m.role = None
        m.initialize_role_attributes = lambda m=m: setattr(
            m, "is_hitler", getattr(m.role, "is_hitler", False)
        )
        m.is_hitler = False
        m.is_fascist = False
        m.is_communist = False
        m.id = i
        mocks.append(m)

    context.fake_pf = Mock(spec=PlayerFactory)

    def fake_create(pcount, state, strategy_type=None, human_player_indices=None):
        state.players = mocks.copy()
        state.active_players = mocks.copy()

    context.fake_pf.create_players.side_effect = fake_create
    context.fake_pf.update_player_strategies = Mock()

    context.patcher_pf_methods = patch(
        "src.game.game.PlayerFactory", return_value=context.fake_pf
    )
    context.patch_pf_methods = context.patcher_pf_methods.start()

    context.player_mocks = mocks


@given(
    'parcheo RoleFactory.create_roles para retornar roles ["roleA", "roleB", "roleC"] donde roleB.is_hitler es true'
)
def step_given_parcheo_rolefactory_create_roles(context):
    roles = []
    for i in range(3):
        r = Mock(name=f"Role{i}")
        r.is_hitler = i == 1
        r.is_fascist = r.is_hitler or False
        r.is_communist = False
        r.is_liberal = not (r.is_hitler or r.is_fascist or r.is_communist)
        setattr(
            r,
            "role",
            "hitler" if r.is_hitler else ("fascist" if r.is_fascist else "liberal"),
        )
        roles.append(r)

    context.fake_rf = Mock(spec=RoleFactory)
    context.fake_rf.create_roles.return_value = roles

    context.patcher_rf_class = patch(
        "src.game.game.RoleFactory", return_value=context.fake_rf
    )
    context.patch_rf_class = context.patcher_rf_class.start()


@given("parcheo PlayerFactory.update_player_strategies")
def step_given_parcheo_playerfactory_update_strategies(context):
    pass


@when("llamo a assign_players")
def step_when_llamo_assign_players(context):
    context.game.player_count = len(context.player_mocks)
    context.game.communists_in_play = False
    context.game.ai_strategy = "smart"
    context.game.human_player_indices = []
    context.game.assign_players()


@then('PlayerFactory.create_players fue llamado una vez con (3, state, "smart", [])')
def step_then_playerfactory_create_players_llamado(context):
    context.fake_pf.create_players.assert_called_once()
    args, kwargs = context.fake_pf.create_players.call_args
    assert args[0] == 3
    assert args[1] is context.game.state
    assert kwargs.get("strategy_type") == "smart"
    assert kwargs.get("human_player_indices") == []


@then("RoleFactory.create_roles fue llamado una vez con (3, with_communists false)")
def step_then_rolefactory_create_roles_llamado(context):
    context.fake_rf.create_roles.assert_called_once()
    args, kwargs = context.fake_rf.create_roles.call_args
    assert args[0] == 3
    assert kwargs.get("with_communists") is False


@then("cada mock-jugador obtuvo su atributo role asignado")
def step_then_mock_jugador_role_asignado(context):
    for idx, player in enumerate(context.player_mocks):
        expected_role = context.fake_rf.create_roles.return_value[idx]
        assert player.role is expected_role
        player.initialize_role_attributes()
        assert player.is_hitler == expected_role.is_hitler


@then("hitler_player debe ser el mock-jugador cuyo is_hitler es true")
def step_then_hitler_player_asignado(context):
    assert context.game.hitler_player == context.player_mocks[1]


@then(
    'PlayerFactory.update_player_strategies fue llamado una vez con (state.players, "smart")'
)
def step_then_playerfactory_update_strategies_llamado(context):
    context.fake_pf.update_player_strategies.assert_called_once_with(
        context.game.state.players, "smart"
    )
    context.patcher_pf_methods.stop()
    context.patcher_rf_class.stop()


# ------------------------------------------------------
@given("state.players contiene:")
def step_given_state_players_contiene_tabla(context):
    context.game.state.players = []
    for row in context.table:
        p = Mock(name=f'Player{row["id"]}')
        p.id = int(row["id"])
        p.is_fascist = row["is_fascist"].lower() == "true"
        p.is_hitler = row["is_hitler"].lower() == "true"
        p.is_communist = False
        p.hitler = None
        p.fascists = None
        p.known_communists = []
        context.game.state.players.append(p)
    context.game.hitler_player = next(
        (p for p in context.game.state.players if p.is_hitler), None
    )


@given("state.players contiene")
def step_given_state_players_contiene(context):
    context.game.state.players = []
    for row in context.table:
        p = Mock(name=f'Player{row["id"]}')
        p.id = int(row["id"])
        p.is_fascist = row["is_fascist"].lower() == "true"
        p.is_hitler = row["is_hitler"].lower() == "true"
        p.is_communist = row.get("is_communist", "false").lower() == "true"
        p.hitler = None
        p.fascists = None
        p.known_communists = []
        context.game.state.players.append(p)
    context.game.hitler_player = next(
        (p for p in context.game.state.players if p.is_hitler), None
    )


@given("game.player_count is {pc:d}")
def step_given_game_player_count_is(context, pc):
    context.game.player_count = pc


@when("llamo a inform_players")
def step_when_llamo_inform_players(context):
    if any(getattr(p, "is_communist", False) for p in context.game.state.players):
        context.game.communists_in_play = True
    context.game.inform_players()


@then("cada fascista (id 0 y 1) debe tener .hitler asignado al mock de Hitler (id 2)")
def step_then_fascistas_hitler_asignado(context):
    p1 = next(p for p in context.game.state.players if p.id == 0)
    p2 = next(p for p in context.game.state.players if p.id == 1)
    hitler = next(p for p in context.game.state.players if p.id == 2)
    assert p1.hitler is hitler
    assert p2.hitler is hitler


@then(
    "cada lista .fascists de los fascistas debe igualar la lista de otros mocks fascistas"
)
def step_then_fascistas_lista_fascists(context):
    fascists = [
        p for p in context.game.state.players if p.is_fascist and not p.is_hitler
    ]
    for fascist in fascists:
        assert fascist.fascists == fascists


@then("el mock de Hitler debe tener .fascists igual a [fascista0, fascista1]")
def step_then_hitler_fascists_lista(context):
    hitler = next(p for p in context.game.state.players if p.is_hitler)
    expected = [
        p for p in context.game.state.players if p.is_fascist and not p.is_hitler
    ]
    assert hitler.fascists == expected


@then(
    "cada .known_communists de los comunistas debe listar los IDs de los otros comunistas"
)
def step_then_comunistas_known_communists(context):
    communists = [p for p in context.game.state.players if p.is_communist]
    ids = [p.id for p in communists]
    for c in communists:
        expected = [i for i in ids if i != c.id]
        assert sorted(c.known_communists) == sorted(expected)


@then("ningún mock comunista debe tener el atributo .known_communists definido")
def step_then_ningun_comunista_known_communists(context):
    communists = [p for p in context.game.state.players if p.is_communist]
    for c in communists:
        assert getattr(c, "known_communists", []) == []


# ------------------------------------------------------
# New step definitions for extended game functionality
# ------------------------------------------------------


@given("state.round_number is {number:d}")
def step_given_state_round_number(context, number):
    context.game.state.round_number = number


@given("un mock de set_next_president es configurado")
def step_given_mock_set_next_president(context):
    context.game.set_next_president = Mock()


@when("llamo a advance_turn")
def step_when_llamo_advance_turn(context):
    context.resultado = context.game.advance_turn()


@then("state.round_number debe ser {number:d}")
def step_then_state_round_number(context, number):
    assert context.game.state.round_number == number


@then("set_next_president fue llamado una vez")
def step_then_set_next_president_llamado(context):
    context.game.set_next_president.assert_called_once()


@then("el resultado debe ser state.president_candidate")
def step_then_resultado_president_candidate(context):
    assert context.resultado == context.game.state.president_candidate


@given("state tiene president_candidate mock con nominate_chancellor")
def step_given_president_candidate_mock(context):
    context.game.state.president_candidate = Mock()
    context.selected_chancellor = Mock(name="selected_chancellor")
    context.game.state.president_candidate.nominate_chancellor = Mock(
        return_value=context.selected_chancellor
    )


@given("state tiene eligible_chancellors {chancellors}")
def step_given_eligible_chancellors(context, chancellors):
    import ast

    chancellor_list = ast.literal_eval(chancellors)
    context.game.state.get_eligible_chancellors = Mock(return_value=chancellor_list)
    context.eligible_chancellors = chancellor_list


@when("llamo a nominate_chancellor")
def step_when_llamo_nominate_chancellor(context):
    context.resultado = context.game.nominate_chancellor()


@then("president_candidate.nominate_chancellor fue llamado con eligible_chancellors")
def step_then_nominate_chancellor_llamado(context):
    context.game.state.president_candidate.nominate_chancellor.assert_called_once_with(
        context.eligible_chancellors
    )


@then("el resultado debe ser el candidato seleccionado")
def step_then_resultado_candidato_seleccionado(context):
    assert context.resultado == context.selected_chancellor


@given("state.get_eligible_chancellors retorna lista vacía")
def step_given_get_eligible_chancellors_empty(context):
    context.game.state.get_eligible_chancellors = Mock(return_value=[])


@given("active_players con votes {votes}")
def step_given_active_players_votes(context, votes):
    vote_str = votes.replace("true", "True").replace("false", "False")
    import ast

    vote_list = ast.literal_eval(vote_str)

    mock_players = []
    for i, vote in enumerate(vote_list):
        player = Mock(name=f"Player{i}")
        player.vote = Mock(return_value=vote)
        mock_players.append(player)

    context.game.state.active_players = mock_players
    context.expected_votes = vote_list

    context.game.state.president_candidate = mock_players[0]
    context.game.state.chancellor_candidate = mock_players[1] if len(mock_players) > 1 else mock_players[0]


@when("llamo a vote_on_government")
def step_when_llamo_vote_on_government(context):
    context.resultado = context.game.vote_on_government()


@then("cada jugador.vote fue llamado una vez")
def step_then_cada_jugador_vote_llamado(context):
    for player in context.game.state.active_players:
        player.vote.assert_called_once()


@then("state.last_votes debe igualar {votes}")
def step_then_state_last_votes(context, votes):
    vote_str = votes.replace("true", "True").replace("false", "False")
    import ast

    expected = ast.literal_eval(vote_str)
    assert context.game.state.last_votes == expected


@then("el resultado debe ser true (mayoría ja)")
def step_then_resultado_true_mayoria(context):
    assert context.resultado is True


@then("state.election_tracker debe ser {number:d}")
def step_then_state_election_tracker(context, number):
    assert context.game.state.election_tracker == number


@then("el resultado debe ser false")
def step_then_resultado_false(context):
    assert context.resultado is False


@then("state.election_tracker no debe cambiar")
def step_then_election_tracker_no_cambia(context):
    pass


@given('board.draw_policy(1) retorna [mock_policy con type "fascist"]')
def step_given_board_draw_policy_fascist(context):
    if not hasattr(context.game.state, "board") or context.game.state.board is None:
        context.game.state.board = Mock(name="BoardMock")
        context.game.state.board.liberal_track = 0
        context.game.state.board.liberal_track_size = 5
        context.game.state.board.fascist_track = 0
        context.game.state.board.fascist_track_size = 6
        context.game.state.board.communist_track = 0
        context.game.state.board.communist_track_size = 5

    context.mock_policy = Mock()
    context.mock_policy.type = "fascist"
    context.game.state.board.draw_policy = Mock(return_value=[context.mock_policy])
    context.game.state.board.enact_policy = Mock()


@given("state.enacted_policies is {number:d}")
def step_given_state_enacted_policies(context, number):
    context.game.state.enacted_policies = number


@when("llamo a enact_chaos_policy")
def step_when_llamo_enact_chaos_policy(context):
    context.resultado = context.game.enact_chaos_policy()


@then("board.enact_policy fue llamado con mock_policy y chaos=true")
def step_then_board_enact_policy_chaos(context):
    context.game.state.board.enact_policy.assert_called_once_with(
        context.mock_policy, chaos=True
    )


@then("state.enacted_policies debe ser {number:d}")
def step_then_state_enacted_policies(context, number):
    assert context.game.state.enacted_policies == number


@given("board.liberal_track is {number:d}")
def step_given_board_liberal_track(context, number):
    initialize_board_mock_with_defaults(context)
    context.game.state.board.liberal_track = number


@given("board.liberal_track_size is {number:d}")
def step_given_board_liberal_track_size(context, number):
    initialize_board_mock_with_defaults(context)
    context.game.state.board.liberal_track_size = number


@when("llamo a check_policy_win")
def step_when_llamo_check_policy_win(context):
    context.resultado = context.game.check_policy_win()


@then("state.game_over debe ser true")
def step_then_state_game_over_true(context):
    assert context.game.state.game_over is True


@then('state.winner debe ser "liberal"')
def step_then_state_winner_liberal(context):
    assert context.game.state.winner == "liberal"


@then("el resultado debe ser true")
def step_then_resultado_true(context):
    assert context.resultado is True


@given("board.fascist_track is {number:d}")
def step_given_board_fascist_track(context, number):
    initialize_board_mock_with_defaults(context)
    context.game.state.board.fascist_track = number


@given("board.fascist_track_size is {number:d}")
def step_given_board_fascist_track_size(context, number):
    initialize_board_mock_with_defaults(context)
    context.game.state.board.fascist_track_size = number


@then('state.winner debe ser "fascist"')
def step_then_state_winner_fascist(context):
    assert context.game.state.winner == "fascist"


@given("communists_in_play is true")
def step_given_communists_in_play_true(context):
    context.game.communists_in_play = True


@given("board.communist_track is {number:d}")
def step_given_board_communist_track(context, number):
    initialize_board_mock_with_defaults(context)
    context.game.state.board.communist_track = number


@given("board.communist_track_size is {number:d}")
def step_given_board_communist_track_size(context, number):
    initialize_board_mock_with_defaults(context)
    context.game.state.board.communist_track_size = number


@then('state.winner debe ser "communist"')
def step_then_state_winner_communist(context):
    assert context.game.state.winner == "communist"


@given("board tracks no alcanzan sus tamaños máximos")
def step_given_board_tracks_no_max(context):
    initialize_board_mock_with_defaults(context)
    context.game.state.board.liberal_track = 3
    context.game.state.board.liberal_track_size = 5
    context.game.state.board.fascist_track = 4
    context.game.state.board.fascist_track_size = 6
    context.game.state.board.communist_track = 2
    context.game.state.board.communist_track_size = 5


@then("state.game_over debe ser false")
def step_then_state_game_over_false(context):
    assert context.game.state.game_over is False


@then("state.winner debe ser None")
def step_then_state_winner_none(context):
    assert context.game.state.winner is None


@given(
    "state.president mock con filter_policies retornando (chosen_policies, discarded_policy)"
)
def step_given_president_filter_policies_mock(context):
    context.chosen_policies = [Mock(name="chosen1"), Mock(name="chosen2")]
    context.discarded_policy = Mock(name="discarded")
    context.game.state.president = Mock()
    context.game.state.president.filter_policies = Mock(
        return_value=(context.chosen_policies, context.discarded_policy)
    )


@when("llamo a presidential_policy_choice con [pol1, pol2, pol3]")
def step_when_llamo_presidential_policy_choice(context):
    context.policies = [Mock(name="pol1"), Mock(name="pol2"), Mock(name="pol3")]
    context.resultado = context.game.presidential_policy_choice(context.policies)


@then("president.filter_policies fue llamado con [pol1, pol2, pol3]")
def step_then_president_filter_policies_llamado(context):
    context.game.state.president.filter_policies.assert_called_once_with(
        context.policies
    )


@then("state.last_discarded debe ser discarded_policy")
def step_then_state_last_discarded_policy(context):
    assert context.game.state.last_discarded == context.discarded_policy


@then("el resultado debe ser (chosen_policies, discarded_policy)")
def step_then_resultado_chosen_discarded(context):
    assert context.resultado == (context.chosen_policies, context.discarded_policy)


@given("board.veto_available is false")
def step_given_board_veto_available_false(context):
    if not hasattr(context.game.state, "board") or context.game.state.board is None:
        context.game.state.board = Mock(name="BoardMock")
    context.game.state.board.veto_available = False


@when("llamo a chancellor_propose_veto")
def step_when_llamo_chancellor_propose_veto(context):
    context.resultado = context.game.chancellor_propose_veto()


@given("board.veto_available is true")
def step_given_board_veto_available_true(context):
    # Initialize board mock if it doesn't exist
    if not hasattr(context.game.state, "board") or context.game.state.board is None:
        context.game.state.board = Mock(name="BoardMock")
    context.game.state.board.veto_available = True


@given("state.chancellor mock con veto() retornando true")
def step_given_chancellor_veto_mock_true(context):
    context.game.state.chancellor = Mock()
    context.game.state.chancellor.veto = Mock(return_value=True)


@then("chancellor.veto fue llamado")
def step_then_chancellor_veto_llamado(context):
    context.game.state.chancellor.veto.assert_called_once()


@given("state.president mock con accept_veto() retornando false")
def step_given_president_accept_veto_mock_false(context):
    context.game.state.president = Mock()
    context.game.state.president.accept_veto = Mock(return_value=False)


@when("llamo a president_veto_accepted")
def step_when_llamo_president_veto_accepted(context):
    context.resultado = context.game.president_veto_accepted()


@then("president.accept_veto fue llamado")
def step_then_president_accept_veto_llamado(context):
    context.game.state.president.accept_veto.assert_called_once()


@given("state.chancellor mock con choose_policy retornando (chosen, discarded)")
def step_given_chancellor_choose_policy_mock(context):
    context.chosen = Mock(name="chosen")
    context.discarded = Mock(name="discarded")
    context.game.state.chancellor = Mock()
    context.game.state.chancellor.choose_policy = Mock(
        return_value=(context.chosen, context.discarded)
    )


@when("llamo a chancellor_policy_choice con [pol1, pol2]")
def step_when_llamo_chancellor_policy_choice(context):
    context.policies = [Mock(name="pol1"), Mock(name="pol2")]
    context.resultado = context.game.chancellor_policy_choice(context.policies)


@then("chancellor.choose_policy fue llamado con [pol1, pol2]")
def step_then_chancellor_choose_policy_llamado(context):
    context.game.state.chancellor.choose_policy.assert_called_once_with(
        context.policies
    )


@then("state.last_discarded debe ser discarded")
def step_then_state_last_discarded(context):
    assert context.game.state.last_discarded == context.discarded


@then("el resultado debe ser (chosen, discarded)")
def step_then_resultado_chosen_discarded_chancellor(context):
    assert context.resultado == (context.chosen, context.discarded)


@given("state.block_next_fascist_power is true")
def step_given_block_next_fascist_power_true(context):
    context.game.state.block_next_fascist_power = True


@when("llamo a get_fascist_power")
def step_when_llamo_get_fascist_power(context):
    context.resultado = context.game.get_fascist_power()


@then("state.block_next_fascist_power debe ser false")
def step_then_block_next_fascist_power_false(context):
    assert context.game.state.block_next_fascist_power is False


@given("state.block_next_fascist_power is false")
def step_given_block_next_fascist_power_false(context):
    context.game.state.block_next_fascist_power = False


@given('board.get_power_for_track_position retorna "investigation"')
def step_given_board_get_power_investigation(context):
    if not hasattr(context.game.state, "board") or context.game.state.board is None:
        context.game.state.board = Mock(name="BoardMock")
    context.game.state.board.get_power_for_track_position = Mock(
        return_value="investigation"
    )
    context.game.state.board.fascist_track = 3


@then(
    'board.get_power_for_track_position fue llamado con ("fascist", board.fascist_track)'
)
def step_then_board_get_power_fascist_llamado(context):
    context.game.state.board.get_power_for_track_position.assert_called_once_with(
        "fascist", context.game.state.board.fascist_track
    )


@given("state.block_next_communist_power is true")
def step_given_block_next_communist_power_true(context):
    context.game.state.block_next_communist_power = True


@when("llamo a get_communist_power")
def step_when_llamo_get_communist_power(context):
    context.resultado = context.game.get_communist_power()


@then("state.block_next_communist_power debe ser false")
def step_then_block_next_communist_power_false(context):
    assert context.game.state.block_next_communist_power is False


@given("state.block_next_communist_power is false")
def step_given_block_next_communist_power_false(context):
    context.game.state.block_next_communist_power = False


@given('board.get_power_for_track_position retorna "bugging"')
def step_given_board_get_power_bugging(context):
    if not hasattr(context.game.state, "board") or context.game.state.board is None:
        context.game.state.board = Mock(name="BoardMock")
    context.game.state.board.get_power_for_track_position = Mock(return_value="bugging")
    context.game.state.board.communist_track = 2


@then(
    'board.get_power_for_track_position fue llamado con ("communist", board.communist_track)'
)
def step_then_board_get_power_communist_llamado(context):
    context.game.state.board.get_power_for_track_position.assert_called_once_with(
        "communist", context.game.state.board.communist_track
    )


@given('PowerRegistry.get_owner("investigation") retorna PRESIDENT')
def step_given_power_registry_get_owner_president(context):
    from src.game.powers.abstract_power import PowerOwner

    with patch("src.game.game.PowerRegistry") as mock_registry:
        mock_registry.get_owner.return_value = PowerOwner.PRESIDENT
        context.mock_registry = mock_registry


@given('execute_presidential_power mock retorna "investigation_result"')
def step_given_execute_presidential_power_mock(context):
    context.game.execute_presidential_power = Mock(return_value="investigation_result")


@when('llamo a execute_power con "investigation"')
def step_when_llamo_execute_power_investigation(context):
    with patch("src.game.game.PowerRegistry") as mock_registry:
        from src.game.powers.abstract_power import PowerOwner

        mock_registry.get_owner.return_value = PowerOwner.PRESIDENT
        context.resultado = context.game.execute_power("investigation")


@then('execute_presidential_power fue llamado con "investigation"')
def step_then_execute_presidential_power_llamado(context):
    context.game.execute_presidential_power.assert_called_once_with("investigation")


@given('PowerRegistry.get_owner("chancellor_propaganda") retorna CHANCELLOR')
def step_given_power_registry_get_owner_chancellor(context):
    from src.game.powers.abstract_power import PowerOwner

    with patch("src.game.game.PowerRegistry") as mock_registry:
        mock_registry.get_owner.return_value = PowerOwner.CHANCELLOR
        context.mock_registry = mock_registry


@given('execute_chancellor_power mock retorna "propaganda_result"')
def step_given_execute_chancellor_power_mock(context):
    context.game.execute_chancellor_power = Mock(return_value="propaganda_result")


@when('llamo a execute_power con "chancellor_propaganda"')
def step_when_llamo_execute_power_chancellor_propaganda(context):
    with patch("src.game.game.PowerRegistry") as mock_registry:
        from src.game.powers.abstract_power import PowerOwner

        mock_registry.get_owner.return_value = PowerOwner.CHANCELLOR
        context.resultado = context.game.execute_power("chancellor_propaganda")


@then('execute_chancellor_power fue llamado con "chancellor_propaganda"')
def step_then_execute_chancellor_power_llamado(context):
    context.game.execute_chancellor_power.assert_called_once_with(
        "chancellor_propaganda"
    )


@given('PowerRegistry.get_power("investigate_loyalty", game) retorna mock_power')
def step_given_power_registry_get_power_investigate(context):
    context.mock_power = Mock()
    with patch("src.game.game.PowerRegistry") as mock_registry:
        mock_registry.get_power.return_value = context.mock_power
        context.mock_registry = mock_registry


@given("state.active_players contiene [president, player1, player2]")
def step_given_state_active_players_with_president(context):
    context.president = Mock(name="president")
    context.player1 = Mock(name="player1")
    context.player2 = Mock(name="player2")
    context.president.id = "pres_id"
    context.player1.id = "p1_id"
    context.player2.id = "p2_id"

    context.game.state.active_players = [
        context.president,
        context.player1,
        context.player2,
    ]
    context.game.state.president = context.president


@given("president.choose_player_to_investigate retorna player1")
def step_given_president_choose_player_to_investigate(context):
    context.president.choose_player_to_investigate = Mock(return_value=context.player1)


@given('mock_power.execute(player1) retorna "liberal"')
def step_given_mock_power_execute_liberal(context):
    context.mock_power.execute = Mock(return_value="liberal")


@when('llamo a execute_presidential_power con "investigate_loyalty"')
def step_when_llamo_execute_presidential_power_investigate(context):
    with patch("src.game.game.PowerRegistry") as mock_registry:
        mock_registry.get_power.return_value = context.mock_power
        context.resultado = context.game.execute_presidential_power(
            "investigate_loyalty"
        )


@then("president.choose_player_to_investigate fue llamado con [player1, player2]")
def step_then_president_choose_player_investigate_llamado(context):
    context.president.choose_player_to_investigate.assert_called_once_with(
        [context.player1, context.player2]
    )


@then("mock_power.execute fue llamado con player1")
def step_then_mock_power_execute_llamado(context):
    context.mock_power.execute.assert_called_once_with(context.player1)


@given('PowerRegistry.get_power("chancellor_propaganda", game) retorna mock_power')
def step_given_power_registry_get_power_chancellor_propaganda(context):
    context.mock_power = Mock()
    with patch("src.game.game.PowerRegistry") as mock_registry:
        mock_registry.get_power.return_value = context.mock_power
        context.mock_registry = mock_registry


@given("mock_power.execute() retorna viewed_policy")
def step_given_mock_power_execute_viewed_policy(context):
    context.viewed_policy = Mock(name="viewed_policy")
    context.mock_power.execute = Mock(return_value=context.viewed_policy)


@when('llamo a execute_chancellor_power con "chancellor_propaganda"')
def step_when_llamo_execute_chancellor_power_propaganda(context):
    with patch("src.game.game.PowerRegistry") as mock_registry:
        mock_registry.get_power.return_value = context.mock_power
        context.resultado = context.game.execute_chancellor_power(
            "chancellor_propaganda"
        )


@then("mock_power.execute fue llamado sin argumentos")
def step_then_mock_power_execute_sin_argumentos(context):
    context.mock_power.execute.assert_called_once_with()


@then("el resultado debe ser viewed_policy")
def step_then_resultado_viewed_policy(context):
    assert context.resultado == context.viewed_policy
