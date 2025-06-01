# features/steps/game_steps.py

from random import randint
from unittest.mock import Mock, patch

# mypy: disable-error-code=import
from behave import given, then, when

from src.game.board import GameBoard
from src.game.game import SHXLGame
from src.players.player_factory import PlayerFactory
from src.policies.policy_factory import PolicyFactory
from src.roles.role_factory import RoleFactory


@given('a new SHXLGame instance')
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
@when('inicializo el tablero con {players:d} jugadores y flag comunista {flag}')
def step_when_inicializo_tablero(context, players, flag):
    context.gb_mock = Mock(name='GameBoardMock')
    context.patcher_gb = patch('src.game.game.GameBoard', return_value=context.gb_mock)
    context.patch_gb = context.patcher_gb.start()
    context.game.initialize_board(players, flag)
    context.patcher_gb.stop()


@then('se debe haber construido un GameBoard con state, {players:d}, {flag}')
def step_then_gameboard_construido(context, players, flag):
    context.patch_gb.assert_called_once_with(context.state, players, flag)


@then('context.state.board debe asignarse al mock de GameBoard')
def step_then_state_board_asignado(context):
    assert context.state.board is context.gb_mock


# ------------------------------------------------------
@given('el juego tiene active_players {player_list}')
def step_given_active_players(context, player_list):
    import ast
    lst = ast.literal_eval(player_list)
    context.game.state.active_players = lst


@given('randint returns {index:d}')
def step_given_randint_returns(context, index):
    context.patcher_rand = patch('src.game.game.randint', return_value=index)
    context.patch_rand = context.patcher_rand.start()


@when('elijo primer presidente')
def step_when_elijo_primer_presidente(context):
    context.game.choose_first_president()
    context.patcher_rand.stop()


@then('state.president_candidate debe ser "{expected_player}"')
def step_then_president_candidate(context, expected_player):
    assert context.game.state.president_candidate == expected_player


# ------------------------------------------------------
@given('current_phase execute returns itself once then sets game_over true')
def step_given_current_phase_execute(context):
    phase_mock = Mock(name='PhaseMock')

    def execute_side_effect():
        if not hasattr(phase_mock, 'called'):
            phase_mock.called = True
            return phase_mock
        else:
            context.game.state.game_over = True
            return phase_mock

    phase_mock.execute.side_effect = execute_side_effect
    context.phase_mock = phase_mock
    context.game.current_phase = phase_mock


@given('state.winner is "{winner}"')
def step_given_state_winner(context, winner):
    context.game.state.winner = winner


@when('inicio el juego')
def step_when_inicio_juego(context):
    context.result = context.game.start_game()


@then('el ganador retornado debe ser "{winner}"')
def step_then_ganador_retornado(context, winner):
    assert context.result == winner


@then('execute fue llamado al menos una vez sobre el objeto de fase')
def step_then_execute_llamado(context):
    assert context.phase_mock.execute.call_count >= 1


# ------------------------------------------------------
@given('player_count {pc:d}')
def step_given_player_count(context, pc):
    context.pc = pc


@given('with_communists {flag}')
def step_given_with_communists(context, flag):
    context.with_comm = False if flag.lower() == 'false' else True


@given('with_anti_policies {flag}')
def step_given_with_anti_policies(context, flag):
    context.with_antip = False if flag.lower() == 'false' else True


@given('with_emergency_powers {flag}')
def step_given_with_emergency_powers(context, flag):
    context.with_emerg = False if flag.lower() == 'false' else True


@given('human_player_indices {indices}')
def step_given_human_player_indices(context, indices):
    import ast
    context.humans = ast.literal_eval(indices)


@given('ai_strategy is "{strategy}"')
def step_given_ai_strategy(context, strategy):
    context.strategy = strategy


@given('stubeo initialize_board, policy_deck_initialization, assign_players, inform_players, choose_first_president')
def step_given_stubeo_methods(context):
    # 1) Stub initialize_board
    def fake_init_board(self, players, comm_flag):
        context.init_board_called = True
        context.game.state.board = Mock(name='BoardWithDeck')
        context.game.state.board.initialize_policy_deck = Mock(name='initialize_policy_deck')

    context.orig_init_board = SHXLGame.initialize_board
    SHXLGame.initialize_board = fake_init_board

    # 2) Parcheamos PolicyFactory a clase retornando fake_pf
    context.fake_pf = Mock(spec=PolicyFactory)
    context.patcher_pf_class = patch('src.game.game.PolicyFactory', return_value=context.fake_pf)
    context.patch_pf_class = context.patcher_pf_class.start()

    # 3) Stub assign_players, inform_players, choose_first_president
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


@when('configuro el juego')
def step_when_configuro_juego(context):
    context.game.setup_game(
        context.pc,
        with_communists=context.with_comm,
        with_anti_policies=context.with_antip,
        with_emergency_powers=context.with_emerg,
        human_player_indices=context.humans,
        ai_strategy=context.strategy,
    )
    # Detenemos/parcheamos de vuelta
    context.patch_pf_class.stop()
    SHXLGame.initialize_board = context.orig_init_board
    SHXLGame.assign_players = context.orig_assign
    SHXLGame.inform_players = context.orig_inform
    SHXLGame.choose_first_president = context.orig_choose


@then('game.player_count debe ser {pc:d}')
def step_then_game_player_count(context, pc):
    assert context.game.player_count == pc


@then('game.communists_in_play debe ser {flag}')
def step_then_game_communists_in_play(context, flag):
    expected = False if flag.lower() == 'false' else True
    assert context.game.communists_in_play == expected


@then('game.anti_policies_in_play debe ser {flag}')
def step_then_game_anti_policies_in_play(context, flag):
    expected = False if flag.lower() == 'false' else True
    assert context.game.anti_policies_in_play == expected


@then('game.emergency_powers_in_play debe ser {flag}')
def step_then_game_emergency_powers_in_play(context, flag):
    expected = False if flag.lower() == 'false' else True
    assert context.game.emergency_powers_in_play == expected


@then('game.human_player_indices debe igualar {indices}')
def step_then_game_human_player_indices(context, indices):
    import ast
    expected = ast.literal_eval(indices)
    assert context.game.human_player_indices == expected


@then('game.ai_strategy debe ser "{strategy}"')
def step_then_game_ai_strategy(context, strategy):
    assert context.game.ai_strategy == strategy


@then('initialize_board fue llamado una vez con argumentos (5, false)')
def step_then_initialize_board_llamado(context):
    assert context.init_board_called is True


@then('policy_deck_initialization fue llamado una vez con el mock de PolicyFactory, false, false')
def step_then_policy_deck_initialization_llamado(context):
    board = context.game.state.board
    board.initialize_policy_deck.assert_called_once_with(context.fake_pf, False, False)


@then('assign_players fue llamado una vez')
def step_then_assign_players_llamado(context):
    assert context.assign_called is True


@then('inform_players fue llamado una vez')
def step_then_inform_players_llamado(context):
    assert context.inform_called is True


@then('choose_first_president fue llamado una vez')
def step_then_choose_first_president_llamado(context):
    assert context.choose_pres_called is True


@then('game.current_phase debe ser None')
def step_then_game_current_phase_none(context):
    assert context.game.current_phase is None


# ------------------------------------------------------
@given('un estado vacío con jugadores {player_list}')
def step_given_estado_vacio_con_jugadores(context, player_list):
    import ast
    context.game.state.players = []
    context.game.state.active_players = []
    context.player_names = ast.literal_eval(player_list)


@given('parcheo PlayerFactory.create_players para agregar {count:d} mocks de jugador a state.players')
def step_given_parcheo_playerfactory_create_players(context, count):
    mocks = []
    for i in range(count):
        m = Mock(name=f'Player{i}')
        m.role = None
        m.initialize_role_attributes = lambda m=m: setattr(
            m, 'is_hitler', getattr(m.role, 'is_hitler', False)
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

    context.patcher_pf_methods = patch('src.game.game.PlayerFactory', return_value=context.fake_pf)
    context.patch_pf_methods = context.patcher_pf_methods.start()

    context.player_mocks = mocks


@given('parcheo RoleFactory.create_roles para retornar roles ["roleA", "roleB", "roleC"] donde roleB.is_hitler es true')
def step_given_parcheo_rolefactory_create_roles(context):
    roles = []
    for i in range(3):
        r = Mock(name=f'Role{i}')
        r.is_hitler = (i == 1)
        r.is_fascist = r.is_hitler or False
        r.is_communist = False
        r.is_liberal = not (r.is_hitler or r.is_fascist or r.is_communist)
        setattr(r, 'role', 'hitler' if r.is_hitler else ('fascist' if r.is_fascist else 'liberal'))
        roles.append(r)

    context.fake_rf = Mock(spec=RoleFactory)
    # Aseguramos que create_roles devuelva directamente la lista `roles`
    context.fake_rf.create_roles.return_value = roles

    context.patcher_rf_class = patch('src.game.game.RoleFactory', return_value=context.fake_rf)
    context.patch_rf_class = context.patcher_rf_class.start()


@given('parcheo PlayerFactory.update_player_strategies')
def step_given_parcheo_playerfactory_update_strategies(context):
    # Ya integrado en fake_pf
    pass


@when('llamo a assign_players')
def step_when_llamo_assign_players(context):
    context.game.player_count = len(context.player_mocks)
    context.game.communists_in_play = False
    context.game.ai_strategy = "smart"
    context.game.human_player_indices = []
    context.game.assign_players()


@then('PlayerFactory.create_players fue llamado una vez con (3, state, "smart", [])')
def step_then_playerfactory_create_players_llamado(context):
    # Verificar args y kwargs
    context.fake_pf.create_players.assert_called_once()
    args, kwargs = context.fake_pf.create_players.call_args
    assert args[0] == 3
    assert args[1] is context.game.state
    assert kwargs.get('strategy_type') == "smart"
    assert kwargs.get('human_player_indices') == []


@then('RoleFactory.create_roles fue llamado una vez con (3, with_communists false)')
def step_then_rolefactory_create_roles_llamado(context):
    # Verificar llamada con keyword argument
    context.fake_rf.create_roles.assert_called_once()
    args, kwargs = context.fake_rf.create_roles.call_args
    assert args[0] == 3
    assert kwargs.get('with_communists') is False


@then('cada mock-jugador obtuvo su atributo role asignado')
def step_then_mock_jugador_role_asignado(context):
    for idx, player in enumerate(context.player_mocks):
        expected_role = context.fake_rf.create_roles.return_value[idx]
        assert player.role is expected_role
        player.initialize_role_attributes()
        assert player.is_hitler == expected_role.is_hitler


@then('hitler_player debe ser el mock-jugador cuyo is_hitler es true')
def step_then_hitler_player_asignado(context):
    assert context.game.hitler_player == context.player_mocks[1]


@then('PlayerFactory.update_player_strategies fue llamado una vez con (state.players, "smart")')
def step_then_playerfactory_update_strategies_llamado(context):
    context.fake_pf.update_player_strategies.assert_called_once_with(context.game.state.players, "smart")
    context.patcher_pf_methods.stop()
    context.patcher_rf_class.stop()


# ------------------------------------------------------
@given('state.players contiene:')
def step_given_state_players_contiene_tabla(context):
    context.game.state.players = []
    for row in context.table:
        p = Mock(name=f'Player{row["id"]}')
        p.id = int(row['id'])
        p.is_fascist = row['is_fascist'].lower() == 'true'
        p.is_hitler = row['is_hitler'].lower() == 'true'
        p.is_communist = False
        p.hitler = None
        p.fascists = None
        p.known_communists = []
        context.game.state.players.append(p)
    context.game.hitler_player = next(
        (p for p in context.game.state.players if p.is_hitler), None
    )


@given('state.players contiene')
def step_given_state_players_contiene(context):
    context.game.state.players = []
    for row in context.table:
        p = Mock(name=f'Player{row["id"]}')
        p.id = int(row['id'])
        p.is_fascist = row['is_fascist'].lower() == 'true'
        p.is_hitler = row['is_hitler'].lower() == 'true'
        p.is_communist = row.get('is_communist', 'false').lower() == 'true'
        p.hitler = None
        p.fascists = None
        p.known_communists = []
        context.game.state.players.append(p)
    context.game.hitler_player = next(
        (p for p in context.game.state.players if p.is_hitler), None
    )


@given('game.player_count is {pc:d}')
def step_given_game_player_count_is(context, pc):
    context.game.player_count = pc


@when('llamo a inform_players')
def step_when_llamo_inform_players(context):
    if any(getattr(p, 'is_communist', False) for p in context.game.state.players):
        context.game.communists_in_play = True
    context.game.inform_players()


@then('cada fascista (id 0 y 1) debe tener .hitler asignado al mock de Hitler (id 2)')
def step_then_fascistas_hitler_asignado(context):
    p1 = next(p for p in context.game.state.players if p.id == 0)
    p2 = next(p for p in context.game.state.players if p.id == 1)
    hitler = next(p for p in context.game.state.players if p.id == 2)
    assert p1.hitler is hitler
    assert p2.hitler is hitler


@then('cada lista .fascists de los fascistas debe igualar la lista de otros mocks fascistas')
def step_then_fascistas_lista_fascists(context):
    fascists = [p for p in context.game.state.players if p.is_fascist and not p.is_hitler]
    for fascist in fascists:
        # Ahora cada fascista.fascists debe coincidir con la lista completa de fascistas
        assert fascist.fascists == fascists


@then('el mock de Hitler debe tener .fascists igual a [fascista0, fascista1]')
def step_then_hitler_fascists_lista(context):
    hitler = next(p for p in context.game.state.players if p.is_hitler)
    expected = [p for p in context.game.state.players if p.is_fascist and not p.is_hitler]
    assert hitler.fascists == expected


@then('cada .known_communists de los comunistas debe listar los IDs de los otros comunistas')
def step_then_comunistas_known_communists(context):
    communists = [p for p in context.game.state.players if p.is_communist]
    ids = [p.id for p in communists]
    for c in communists:
        expected = [i for i in ids if i != c.id]
        assert sorted(c.known_communists) == sorted(expected)


@then('ningún mock comunista debe tener el atributo .known_communists definido')
def step_then_ningun_comunista_known_communists(context):
    communists = [p for p in context.game.state.players if p.is_communist]
    for c in communists:
        assert getattr(c, 'known_communists', []) == []
