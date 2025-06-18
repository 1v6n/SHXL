from unittest.mock import MagicMock, patch

from behave import given, then, when
from src.game.powers.abstract_power import (
    Bugging,
    Confession,
    Congress,
    Execution,
    FiveYearPlan,
    Impeachment,
    InvestigateLoyalty,
    PolicyPeek,
    Propaganda,
    Radicalization,
    SpecialElection,
)

# —————————————————————————————————————————
# DUMMY CLASES PARA MOCKEAR MÍNIMAMENTE
# —————————————————————————————————————————


class DummyRole:
    """Simula el rol de un jugador"""

    def __init__(self, party_membership):
        self.party_membership = party_membership


class DummyPlayer:
    """
    Simula un jugador con todos los atributos necesarios
    """

    def __init__(self, pid, party, is_hitler=False):
        self.id = pid
        self.role = DummyRole(party)
        self.is_dead = False
        self.known_affiliations = {}
        self.known_communists = []
        self.is_hitler = is_hitler
        self._propaganda_always_discard = False

    def propaganda_decision(self, policy):
        return self._propaganda_always_discard


class DummyBoard:
    """
    Simula el board con una lista de políticas y método discard
    """

    def __init__(self, policies):
        self.policies = list(policies)
        self.discarded = []

    def discard(self, policy):
        self.discarded.append(policy)


class DummyState:
    """
    Simula el state del juego con todos los atributos necesarios
    """

    def __init__(self):
        self.investigated_players = []
        self.special_election = False
        self.special_election_return_index = None
        self.president = None
        self.president_candidate = None
        self.board = DummyBoard([])
        self.active_players = []
        self.revealed_affiliations = {}
        self.players = []


class DummyGame:
    """
    Simula la clase principal de juego
    """

    def __init__(self):
        self.state = DummyState()


# Mock classes for policies
class MockCommunist:
    def __str__(self):
        return "Communist"

    def __repr__(self):
        return "Communist"


class MockLiberal:
    def __str__(self):
        return "Liberal"

    def __repr__(self):
        return "Liberal"


# —————————————————————————————————————————
# STEP DEFINITIONS
# —————————————————————————————————————————


# --------------------------
# InvestigateLoyalty
# --------------------------
@given('un "game" mock con estado vacío para investigar')
def step_investigate_given_empty_game(context):
    context.game = DummyGame()
    context.game.state.investigated_players.clear()


@given('un jugador objetivo con party_membership "{party}"')
def step_investigate_given_target_player(context, party):
    context.target = DummyPlayer(pid=99, party=party)


@when("ejecuto InvestigateLoyalty sobre ese jugador")
def step_investigate_when_execute(context):
    power = InvestigateLoyalty(context.game)
    context.resultado = power.execute(context.target)


@then('el resultado debe ser "{value}"')
def step_then_result_equals(context, value):
    assert context.resultado == value, f"Expected {value}, got {context.resultado}"


@then("el estado investigado debe contener al mismo jugador")
def step_investigate_then_contains_player(context):
    assert context.target in context.game.state.investigated_players


# --------------------------
# SpecialElection
# --------------------------
@given('un "game" mock con un presidente actual que tiene id {pid:d}')
def step_special_election_given_president(context, pid):
    context.game = DummyGame()
    pres = DummyPlayer(pid=pid, party="fascist")
    context.game.state.president = pres


@given("la lista special_election_return_index es None")
def step_special_election_given_return_none(context):
    context.game.state.special_election_return_index = None


@when("ejecuto SpecialElection nominando al jugador mock con id {next_pid:d}")
def step_special_election_when_execute(context, next_pid):
    context.next_president = DummyPlayer(pid=next_pid, party="liberal")
    power = SpecialElection(context.game)
    context.resultado = power.execute(context.next_president)


@then("game.state.special_election debe ser true")
def step_special_election_then_flag_true(context):
    assert context.game.state.special_election is True


@then("game.state.president_candidate debe ser ese jugador con id {exp_pid:d}")
def step_special_election_then_candidate_set(context, exp_pid):
    candidato = context.game.state.president_candidate
    assert candidato is not None
    assert candidato.id == exp_pid


@then("game.state.special_election_return_index debe quedar en {orig_pid:d}")
def step_special_election_then_return_index(context, orig_pid):
    assert context.game.state.special_election_return_index == orig_pid


# --------------------------
# PolicyPeek
# --------------------------
@given('un "game" mock con board policies "{policies_str}"')
def step_policy_peek_given_board(context, policies_str):
    context.game = DummyGame()
    policies = policies_str.split(",")
    context.game.state.board = DummyBoard(policies)


@when("ejecuto PolicyPeek")
def step_policy_peek_when_execute(context):
    power = PolicyPeek(context.game)
    context.resultado = power.execute()


@then('el resultado PolicyPeek debe ser "{expected_str}"')
def step_policy_peek_then_result(context, expected_str):
    expected = expected_str.split(",")
    assert (
        context.resultado == expected
    ), f"Expected {expected}, got {context.resultado}"


@then("la pila original debe seguir siendo de tamaño {size:d}")
def step_policy_peek_then_size_unchanged(context, size):
    assert len(context.game.state.board.policies) == size


# --------------------------
# Execution
# --------------------------
@given('un "game" mock con active_players con ids "{ids_str}"')
def step_execution_given_active_players(context, ids_str):
    context.game = DummyGame()
    ids = [int(x.strip()) for x in ids_str.split(",")]
    players = []
    for pid in ids:
        player = DummyPlayer(pid=pid, party="liberal")
        players.append(player)
    context.game.state.active_players = players
    context.game.state.players = players


@given("el jugador con id {pid:d} está vivo inicialmente")
def step_execution_given_player_alive(context, pid):
    for player in context.game.state.active_players:
        if player.id == pid:
            player.is_dead = False
            context.target_player = player
            break


@when("ejecuto Execution sobre el jugador con id {pid:d}")
def step_execution_when_execute(context, pid):
    target = None
    for player in context.game.state.active_players:
        if player.id == pid:
            target = player
            break

    power = Execution(context.game)
    context.resultado = power.execute(target)


@then("el jugador con id {pid:d} debe estar muerto")
def step_execution_then_player_dead(context, pid):
    for player in context.game.state.players:
        if player.id == pid:
            assert player.is_dead is True
            break


@then("el jugador con id {pid:d} no debe estar en active_players")
def step_execution_then_not_in_active(context, pid):
    active_ids = [p.id for p in context.game.state.active_players]
    assert pid not in active_ids


# --------------------------
# Confession
# --------------------------
@given('un "game" mock cuyo president tiene id {pid:d} y party_membership "{party}"')
def step_confession_given_president(context, pid, party):
    context.game = DummyGame()
    pres = DummyPlayer(pid=pid, party=party)
    context.game.state.president = pres
    context.game.state.revealed_affiliations = {}


@when("ejecuto Confession")
def step_confession_when_execute(context):
    power = Confession(context.game)
    context.resultado = power.execute()


@then('game.state.revealed_affiliations con id {pid:d} debe ser "{party}"')
def step_confession_then_revealed(context, pid, party):
    assert context.game.state.revealed_affiliations[pid] == party


# --------------------------
# Bugging
# --------------------------
@given(
    'un "game" mock con jugadores comunistas ids "{comm_ids}" y objetivo id {tid:d} con party "{tparty}"'
)
def step_bugging_given_players(context, comm_ids, tid, tparty):
    context.game = DummyGame()

    # Crear jugadores comunistas
    communist_ids = [int(x.strip()) for x in comm_ids.split(",")]
    players = []

    for cid in communist_ids:
        players.append(DummyPlayer(pid=cid, party="communist"))

    # Crear jugador objetivo
    target = DummyPlayer(pid=tid, party=tparty)
    players.append(target)

    context.game.state.players = players
    context.target = target


@when("ejecuto Bugging sobre el jugador objetivo")
def step_bugging_when_execute(context):
    power = Bugging(context.game)
    context.resultado = power.execute(context.target)


@then('cada jugador comunista debe conocer la afiliación del objetivo como "{tparty}"')
def step_bugging_then_known_affiliations(context, tparty):
    target_id = context.target.id
    for player in context.game.state.players:
        if player.role.party_membership == "communist":
            assert target_id in player.known_affiliations
            assert player.known_affiliations[target_id] == tparty


# --------------------------
# FiveYearPlan
# --------------------------
@when("ejecuto FiveYearPlan")
def step_five_year_plan_when_execute(context):
    # Mock the policy classes
    with patch("src.policies.policy.Communist", MockCommunist), patch(
        "src.policies.policy.Liberal", MockLiberal
    ):
        power = FiveYearPlan(context.game)
        context.resultado = power.execute()


@then("el mazo debe tener {total:d} cartas en total")
def step_five_year_plan_then_total_cards(context, total):
    assert len(context.game.state.board.policies) == total


@then("las primeras tres cartas deben ser communist, communist, liberal")
def step_five_year_plan_then_top_three(context):
    top3 = context.game.state.board.policies[:3]
    expected_types = [MockCommunist, MockCommunist, MockLiberal]
    for i, (actual, expected_type) in enumerate(zip(top3, expected_types)):
        assert isinstance(
            actual, expected_type
        ), f"Position {i}: expected {expected_type}, got {type(actual)}"


# --------------------------
# Congress
# --------------------------
@given('un "game" mock con jugadores de partidos')
def step_congress_given_players(context):
    context.game = DummyGame()
    players = []
    for row in context.table:
        pid = int(row["id"])
        party = row["party"]
        players.append(DummyPlayer(pid=pid, party=party))
    context.game.state.players = players


@when("ejecuto Congress")
def step_congress_when_execute(context):
    power = Congress(context.game)
    context.resultado = power.execute()


@then('el resultado Congress debe contener ids "{expected_str}"')
def step_congress_then_result_contains(context, expected_str):
    expected_ids = [int(x.strip()) for x in expected_str.split(",")]
    assert sorted(context.resultado) == sorted(expected_ids)


@then('cada jugador comunista debe conocer a los comunistas "{expected_str}"')
def step_congress_then_communists_know(context, expected_str):
    expected_ids = [int(x.strip()) for x in expected_str.split(",")]
    for player in context.game.state.players:
        if player.role.party_membership == "communist":
            assert sorted(player.known_communists) == sorted(expected_ids)


# --------------------------
# Radicalization
# --------------------------
@given('un "game" mock con un jugador target id {pid:d} que no es Hitler')
def step_radicalization_given_non_hitler(context, pid):
    context.game = DummyGame()
    context.target = DummyPlayer(pid=pid, party="liberal", is_hitler=False)
    context.game.state.players = [context.target]


@given('un "game" mock con un jugador target id {pid:d} que es Hitler')
def step_radicalization_given_hitler(context, pid):
    context.game = DummyGame()
    context.target = DummyPlayer(pid=pid, party="fascist", is_hitler=True)
    context.game.state.players = [context.target]


@given('el target tiene party_membership "{party}"')
def step_radicalization_given_party(context, party):
    context.target.role.party_membership = party


@when("ejecuto Radicalization sobre ese jugador")
def step_radicalization_when_execute(context):
    # Mock the Communist role class
    mock_communist_role = MagicMock()
    mock_communist_role.return_value.party_membership = "communist"

    with patch("src.policies.policy.Communist", mock_communist_role):
        power = Radicalization(context.game)
        context.resultado = power.execute(context.target)


@then("el resultado no debe ser None")
def step_then_result_not_none(context):
    assert context.resultado is not None


@then('el target debe tener party_membership "{party}"')
def step_radicalization_then_party_changed(context, party):
    assert context.target.role.party_membership == party


@then("el resultado debe ser None")
def step_then_result_is_none(context):
    assert context.resultado is None


@then('el target debe seguir con party_membership "{party}"')
def step_radicalization_then_party_unchanged(context, party):
    assert context.target.role.party_membership == party


# --------------------------
# Propaganda
# --------------------------
@given("el presidente siempre decide descartar en propaganda")
def step_propaganda_given_president_discards(context):
    if hasattr(context.game.state, "president") and context.game.state.president:
        context.game.state.president._propaganda_always_discard = True
    else:
        # Crear presidente si no existe
        pres = DummyPlayer(pid=4, party="fascist")
        pres._propaganda_always_discard = True
        context.game.state.president = pres


@when("ejecuto Propaganda")
def step_propaganda_when_execute(context):
    power = Propaganda(context.game)
    context.resultado = power.execute()


@then('la primera carta del mazo debe ser "{next_top}"')
def step_propaganda_then_top_card(context, next_top):
    assert len(context.game.state.board.policies) > 0
    assert context.game.state.board.policies[0] == next_top


# --------------------------
# Impeachment
# --------------------------
@given(
    'un "game" mock con jugador target id {tid:d} party "{tparty}" y revealer id {rid:d}'
)
def step_impeachment_given_players(context, tid, tparty, rid):
    context.game = DummyGame()
    context.target = DummyPlayer(pid=tid, party=tparty)
    context.revealer = DummyPlayer(pid=rid, party="liberal")
    context.game.state.players = [context.target, context.revealer]


@when("ejecuto Impeachment del target al revealer")
def step_impeachment_when_execute(context):
    power = Impeachment(context.game)
    context.resultado = power.execute(context.target, context.revealer)


@then("el método debe devolver True")
def step_then_result_is_true(context):
    assert context.resultado is True


@then('el revealer debe conocer la afiliación del target como "{tparty}"')
def step_impeachment_then_revealer_knows(context, tparty):
    target_id = context.target.id
    assert target_id in context.revealer.known_affiliations
    assert context.revealer.known_affiliations[target_id] == tparty
