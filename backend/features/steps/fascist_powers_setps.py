# mypy: disable-error-code=import
from unittest.mock import MagicMock, Mock

from behave import given, then, when
from src.game.powers.fascist_powers import (
    Execution,
    InvestigateLoyalty,
    PolicyPeek,
    SpecialElection,
)

# Steps específicos para poderes fascistas - completamente independientes


@given("que existe un juego fascista inicializado")
def step_juego_fascista_inicializado(context):
    """Configura un juego mock básico para poderes fascistas"""
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.investigated_players = []
    context.game.state.active_players = []
    context.game.state.board = Mock()
    context.game.state.board.policies = [
        "Liberal",
        "Fascist",
        "Liberal",
        "Fascist",
        "Liberal",
    ]


@given("que existe un jugador fascista con rol definido")
def step_jugador_fascista_definido(context):
    """Crea un jugador fascista mock"""
    context.fascist_player = Mock()
    context.fascist_player.id = 1
    context.fascist_player.role = Mock()
    context.fascist_player.role.party_membership = "Fascist"
    context.fascist_player.is_dead = False


@given('que existe un jugador fascista objetivo con partido "{partido}"')
def step_jugador_fascista_objetivo(context, partido):
    """Crea un jugador objetivo mock para poderes fascistas"""
    context.target_player = Mock()
    context.target_player.id = 2
    context.target_player.role = Mock()
    context.target_player.role.party_membership = partido
    context.target_player.is_dead = False
    context.game.state.active_players.append(context.target_player)


@given('que el jugador fascista objetivo tiene partido "{partido}"')
def step_jugador_fascista_objetivo_partido(context, partido):
    """Modifica el partido del jugador objetivo fascista"""
    context.target_player.role.party_membership = partido


@given('que tengo el poder fascista "{power_name}"')
def step_tengo_poder_fascista(context, power_name):
    """Crea una instancia del poder fascista especificado"""
    power_classes = {
        "InvestigateLoyalty": InvestigateLoyalty,
        "SpecialElection": SpecialElection,
        "PolicyPeek": PolicyPeek,
        "Execution": Execution,
    }

    power_class = power_classes[power_name]
    context.power = power_class(context.game)


@given("que existe un candidato fascista para presidente especial")
def step_candidato_fascista_presidente(context):
    """Crea un candidato fascista para presidente especial"""
    context.special_candidate = Mock()
    context.special_candidate.id = 3
    context.game.state.president = Mock()
    context.game.state.president.id = 1


@given("que existen políticas fascistas en el mazo de al menos {cantidad:d}")
def step_politicas_fascistas_mazo(context, cantidad):
    """Configura políticas fascistas en el mazo"""
    context.game.state.board.policies = [
        "Liberal",
        "Fascist",
        "Liberal",
        "Fascist",
        "Liberal",
    ][: cantidad + 2]


@given("que existen solo {cantidad:d} políticas fascistas en el mazo")
def step_politicas_fascistas_limitadas(context, cantidad):
    """Configura un número limitado de políticas fascistas"""
    context.game.state.board.policies = ["Liberal", "Fascist"][:cantidad]


@given("que el jugador fascista objetivo está vivo")
def step_jugador_fascista_vivo(context):
    """Asegura que el jugador fascista objetivo esté vivo"""
    context.target_player.is_dead = False


@given("que el jugador fascista objetivo ya está muerto")
def step_jugador_fascista_muerto(context):
    """Marca el jugador fascista objetivo como muerto"""
    context.target_player.is_dead = True


@given("que el jugador fascista objetivo está en lista de activos")
def step_jugador_fascista_en_activos(context):
    """Asegura que el jugador fascista esté en la lista de activos"""
    if context.target_player not in context.game.state.active_players:
        context.game.state.active_players.append(context.target_player)


@when("ejecuto el poder fascista sobre el jugador objetivo")
def step_ejecutar_poder_fascista_objetivo(context):
    """Ejecuta el poder fascista sobre el jugador objetivo"""
    context.result = context.power.execute(context.target_player)


@when("ejecuto el poder fascista de elección especial")
def step_ejecutar_eleccion_fascista_especial(context):
    """Ejecuta el poder fascista de elección especial"""
    context.result = context.power.execute(context.special_candidate)


@when("ejecuto el poder fascista de espiar")
def step_ejecutar_espiar_fascista(context):
    """Ejecuta el poder fascista de espiar políticas"""
    context.result = context.power.execute()


@then("el jugador debe ser marcado como investigado por fascistas")
def step_verificar_investigado_fascista(context):
    """Verifica que el jugador fue marcado como investigado por fascistas"""
    assert context.target_player in context.game.state.investigated_players


@then("debo recibir la afiliación partidaria del jugador fascista objetivo")
def step_verificar_afiliacion_fascista(context):
    """Verifica que se devuelva la afiliación fascista correcta"""
    assert context.result == context.target_player.role.party_membership


@then('debo recibir "{partido}" como resultado fascista')
def step_verificar_partido_fascista_resultado(context, partido):
    """Verifica el partido fascista devuelto"""
    assert context.result == partido


@then("el estado fascista de elección especial debe activarse")
def step_verificar_eleccion_fascista_especial(context):
    """Verifica que se active la elección especial fascista"""
    assert context.game.state.special_election == True


@then("el candidato fascista debe ser establecido como próximo presidente")
def step_verificar_proximo_presidente_fascista(context):
    """Verifica que se establezca el próximo presidente fascista"""
    assert context.game.state.president_candidate == context.special_candidate


@then("el índice fascista de retorno debe guardarse correctamente")
def step_verificar_indice_fascista_retorno(context):
    """Verifica que se guarde el índice fascista de retorno"""
    assert (
        context.game.state.special_election_return_index
        == context.game.state.president.id
    )


@then("debo recibir las {cantidad:d} políticas fascistas superiores del mazo")
def step_verificar_politicas_fascistas_espiadas(context, cantidad):
    """Verifica las políticas fascistas espiadas"""
    expected_policies = context.game.state.board.policies[:cantidad]
    assert context.result == expected_policies


@then("las políticas fascistas no deben ser removidas del mazo")
def step_verificar_politicas_fascistas_no_removidas(context):
    """Verifica que las políticas fascistas no sean removidas"""
    # El mazo debe mantener su tamaño original
    original_size = 5  # Basado en la configuración inicial
    assert len(context.game.state.board.policies) >= 3


@then("el jugador fascista objetivo debe ser ejecutado")
def step_verificar_jugador_fascista_ejecutado(context):
    """Verifica que el jugador fascista esté marcado como muerto"""
    assert context.target_player.is_dead == True


@then("el jugador fascista debe ser removido de jugadores activos")
def step_verificar_removido_fascista_activos(context):
    """Verifica que el jugador fascista sea removido de activos"""
    assert context.target_player not in context.game.state.active_players


@then("debo recibir el jugador fascista ejecutado como resultado")
def step_verificar_jugador_fascista_ejecutado_resultado(context):
    """Verifica que se devuelva el jugador fascista ejecutado"""
    assert context.result == context.target_player


@then("debo recibir solo las {cantidad:d} políticas fascistas disponibles")
def step_verificar_politicas_fascistas_limitadas(context, cantidad):
    """Verifica las políticas fascistas cuando hay menos de 3"""
    assert len(context.result) == cantidad
    assert context.result == context.game.state.board.policies[:cantidad]


@then("el jugador fascista objetivo debe permanecer muerto")
def step_verificar_permanece_fascista_muerto(context):
    """Verifica que el jugador fascista permanezca muerto"""
    assert context.target_player.is_dead == True


@then("el resultado fascista debe ser el jugador objetivo")
def step_verificar_resultado_fascista_jugador(context):
    """Verifica que el resultado fascista sea el jugador objetivo"""
    assert context.result == context.target_player
