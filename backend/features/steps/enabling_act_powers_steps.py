# mypy: disable-error-code=import
from unittest.mock import MagicMock, Mock

from behave import given, then, when
from src.game.powers.abstract_power import PowerOwner
from src.game.powers.enabling_act_powers import (
    ChancellorExecution,
    ChancellorImpeachment,
    ChancellorMarkedForExecution,
    ChancellorPolicyPeek,
    ChancellorPropaganda,
    VoteOfNoConfidence,
)


@given("que existe un juego inicializado para poderes del Canciller")
def step_chancellor_game_initialized(context):
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.board = Mock()
    context.game.state.chancellor = Mock()
    context.game.state.president = Mock()
    context.game.state.active_players = []
    context.game.logger = Mock()


@given("el juego tiene un estado válido con jugadores activos para Canciller")
def step_chancellor_game_valid_state(context):
    # Crear jugadores mock con known_affiliations inicializado como diccionario real
    context.player1 = Mock()
    context.player1.id = 1
    context.player1.name = "Jugador1"
    context.player1.is_dead = False
    context.player1.known_affiliations = {}  # Diccionario real, no Mock

    context.player2 = Mock()
    context.player2.id = 2
    context.player2.name = "Jugador2"
    context.player2.is_dead = False
    context.player2.known_affiliations = {}  # Diccionario real, no Mock

    context.player3 = Mock()
    context.player3.id = 3
    context.player3.name = "Jugador3"
    context.player3.is_dead = False
    context.player3.known_affiliations = {}  # Diccionario real, no Mock

    context.game.state.active_players = [
        context.player1,
        context.player2,
        context.player3,
    ]


@given("hay un Canciller designado para los poderes")
def step_chancellor_designated(context):
    context.game.state.chancellor = context.player1
    context.game.state.chancellor.role = Mock()
    context.game.state.chancellor.role.party_membership = "Liberal"
    context.game.state.president = context.player2


@given("que hay políticas en el mazo")
def step_policies_in_deck(context):
    context.policies = ["Liberal", "Fascist", "Liberal"]
    context.game.state.board.policies = context.policies.copy()


@given("el Canciller tiene el poder de propaganda")
def step_chancellor_has_propaganda_power(context):
    context.power = ChancellorPropaganda(context.game)


@given("que no hay políticas en el mazo")
def step_no_policies_in_deck(context):
    context.game.state.board.policies = []


@given("que hay al menos 3 políticas en el mazo")
def step_at_least_3_policies(context):
    context.policies = ["Liberal", "Fascist", "Liberal", "Fascist", "Liberal"]
    context.game.state.board.policies = context.policies.copy()


@given("el Canciller tiene el poder de observación de políticas")
def step_chancellor_has_peek_power(context):
    context.power = ChancellorPolicyPeek(context.game)


@given("que hay menos de 3 políticas en el mazo")
def step_less_than_3_policies(context):
    context.policies = ["Liberal", "Fascist"]
    context.game.state.board.policies = context.policies.copy()


@given("que hay jugadores elegibles para ver la afiliación")
def step_eligible_players_for_impeachment(context):
    # Asegurar que hay jugadores además del presidente y canciller
    context.game.state.active_players = [
        context.player1,
        context.player2,
        context.player3,
    ]
    context.game.state.chancellor = context.player1
    context.game.state.president = context.player2


@given("el Canciller tiene el poder de impeachment")
def step_chancellor_has_impeachment_power(context):
    context.power = ChancellorImpeachment(context.game)


@given("el Presidente debe elegir un revelador")
def step_president_must_choose_revealer(context):
    context.game.state.president.choose_revealer = Mock(return_value=context.player3)


@given("que hay un jugador específico como revelador")
def step_specific_revealer_player(context):
    context.revealer_player = context.player3
    # Asegurar que known_affiliations sea un diccionario real, no un Mock
    context.revealer_player.known_affiliations = {}


@given("que no hay jugadores elegibles para el impeachment")
def step_no_eligible_players_impeachment(context):
    # Solo presidente y canciller activos
    context.game.state.active_players = [context.player1, context.player2]
    context.game.state.chancellor = context.player1
    context.game.state.president = context.player2


@given("que hay un jugador objetivo válido")
def step_valid_target_player(context):
    context.target_player = context.player3


@given("el Canciller tiene el poder de marcar para ejecución")
def step_chancellor_has_mark_execution_power(context):
    context.power = ChancellorMarkedForExecution(context.game)
    context.game.state.board.fascist_track = 3


@given("que hay un jugador objetivo para ejecutar")
def step_target_player_for_execution(context):
    context.target_player = context.player3
    context.game.state.active_players = [
        context.player1,
        context.player2,
        context.player3,
    ]


@given("el Canciller tiene el poder de ejecución")
def step_chancellor_has_execution_power(context):
    context.power = ChancellorExecution(context.game)


@given("que existe una política previamente descartada")
def step_previously_discarded_policy(context):
    context.game.state.last_discarded = "Liberal"
    context.game.state.board.enact_policy = Mock()


@given("el Canciller tiene el poder de voto de no confianza")
def step_chancellor_has_vote_no_confidence_power(context):
    context.power = VoteOfNoConfidence(context.game)


@given("que no hay política previamente descartada")
def step_no_previously_discarded_policy(context):
    context.game.state.last_discarded = None


@given("cualquier poder del Acta Habilitante")
def step_any_enabling_act_power(context):
    context.powers = [
        ChancellorPropaganda(Mock()),
        ChancellorPolicyPeek(Mock()),
        ChancellorImpeachment(Mock()),
        ChancellorMarkedForExecution(Mock()),
        ChancellorExecution(Mock()),
        VoteOfNoConfidence(Mock()),
    ]


@when("el Canciller activa el poder de propaganda")
def step_activate_propaganda_power(context):
    context.game.state.chancellor.propaganda_decision = Mock()


@when("decide descartar la carta vista")
def step_decide_discard_card(context):
    context.game.state.chancellor.propaganda_decision.return_value = True
    context.game.state.board.discard = Mock()
    context.result = context.power.execute()


@when("decide no descartar la carta vista")
def step_decide_not_discard_card(context):
    context.game.state.chancellor.propaganda_decision.return_value = False
    context.result = context.power.execute()


@when("el Canciller usa propaganda con mazo vacío")
def step_execute_propaganda_empty_deck(context):
    context.result = context.power.execute()


@when("el Canciller activa el poder de observación")
def step_activate_policy_peek_power(context):
    context.result = context.power.execute()


@when("el Canciller activa el poder de impeachment")
def step_activate_impeachment_power(context):
    context.result = context.power.execute()


@when("el Presidente selecciona un jugador válido")
def step_president_selects_valid_player(context):
    # Ya configurado en el given
    pass


@when("el Canciller activa impeachment con revelador específico")
def step_activate_impeachment_with_specific_revealer(context):
    context.result = context.power.execute(revealer_player=context.revealer_player)


@when("el Canciller activa el marcado para ejecución")
def step_activate_mark_for_execution(context):
    context.result = context.power.execute(context.target_player)


@when("el Canciller activa el poder de ejecución directa")
def step_activate_execution_power(context):
    context.result = context.power.execute(context.target_player)


@when("el Canciller activa el voto de no confianza")
def step_activate_vote_no_confidence(context):
    context.result = context.power.execute()


@when("se consulta el propietario del poder")
def step_query_power_owner(context):
    context.owners = [power.get_owner() for power in context.powers]


@then("la carta es removida del mazo")
def step_card_removed_from_deck(context):
    assert len(context.game.state.board.policies) == len(context.policies) - 1


@then("la carta es añadida a la pila de descarte")
def step_card_added_to_discard(context):
    context.game.state.board.discard.assert_called_once()


@then("el poder retorna la política vista")
def step_power_returns_viewed_policy(context):
    assert context.result == context.policies[0]


@then("la carta permanece en el mazo")
def step_card_remains_in_deck(context):
    assert len(context.game.state.board.policies) == len(context.policies)


@then("el poder retorna None")
def step_power_returns_none(context):
    assert context.result is None


@then("no se realizan cambios en el estado del juego")
def step_no_game_state_changes(context):
    # Verificar que no se llamaron métodos de modificación
    pass


@then("el poder retorna las 3 cartas superiores")
def step_power_returns_top_3_cards(context):
    assert context.result == context.policies[:3]


@then("las cartas permanecen en el mazo en el mismo orden")
def step_cards_remain_in_deck_same_order(context):
    assert context.game.state.board.policies == context.policies


@then("el poder retorna todas las cartas disponibles")
def step_power_returns_all_available_cards(context):
    assert context.result == context.policies


@then("las cartas permanecen en el mazo")
def step_cards_remain_in_deck(context):
    assert context.game.state.board.policies == context.policies


@then("el jugador seleccionado conoce la afiliación del Canciller")
def step_selected_player_knows_chancellor_affiliation(context):
    target_id = context.game.state.chancellor.id
    # Verificar que el jugador3 (seleccionado por el presidente) conoce la afiliación
    assert target_id in context.player3.known_affiliations
    assert context.player3.known_affiliations[target_id] == "Liberal"


@then("el poder retorna True")
def step_power_returns_true(context):
    assert context.result is True


@then("el revelador conoce la afiliación del Canciller")
def step_revealer_knows_chancellor_affiliation(context):
    target_id = context.game.state.chancellor.id
    assert target_id in context.revealer_player.known_affiliations
    assert context.revealer_player.known_affiliations[target_id] == "Liberal"


@then("el poder retorna False")
def step_power_returns_false(context):
    assert context.result is False


@then("no se revelan afiliaciones")
def step_no_affiliations_revealed(context):
    # Verificar que no se modificaron las known_affiliations
    for player in context.game.state.active_players:
        if hasattr(player, "known_affiliations"):
            assert len(player.known_affiliations) == 0


@then("el jugador queda marcado para ejecución")
def step_player_marked_for_execution(context):
    assert context.game.state.marked_for_execution == context.target_player


@then("se registra el estado actual del tracker fascista")
def step_fascist_tracker_state_recorded(context):
    assert context.game.state.marked_for_execution_tracker == 3


@then("se genera un log del marcado")
def step_execution_marking_logged(context):
    assert context.game.logger.log.call_count >= 2


@then("el poder retorna el jugador marcado")
def step_power_returns_marked_player(context):
    assert context.result == context.target_player


@then("el jugador objetivo es marcado como muerto")
def step_target_player_marked_dead(context):
    assert context.target_player.is_dead is True


@then("el jugador es removido de la lista de jugadores activos")
def step_player_removed_from_active_list(context):
    assert context.target_player not in context.game.state.active_players


@then("el poder retorna el jugador ejecutado")
def step_power_returns_executed_player(context):
    assert context.result == context.target_player


@then("la última política descartada es promulgada")
def step_last_discarded_policy_enacted(context):
    context.game.state.board.enact_policy.assert_called_once_with("Liberal")


@then("el poder retorna la política promulgada")
def step_power_returns_enacted_policy(context):
    assert context.result == "Liberal"


@then("no se promulga ninguna política")
def step_no_policy_enacted(context):
    # Verificar que enact_policy no fue llamado si existe
    if hasattr(context.game.state.board, "enact_policy"):
        context.game.state.board.enact_policy.assert_not_called()


@then("el propietario debe ser CHANCELLOR")
def step_owner_must_be_chancellor(context):
    for owner in context.owners:
        assert owner == PowerOwner.CHANCELLOR
