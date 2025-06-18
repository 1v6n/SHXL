from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.game.powers.abstract_power import (
    Bugging,
    Confession,
    Congress,
    Execution,
    FiveYearPlan,
    InvestigateLoyalty,
    PolicyPeek,
    PowerOwner,
    Radicalization,
    SpecialElection,
)
from src.game.powers.article48_powers import (
    PresidentialExecution,
    PresidentialImpeachment,
    PresidentialMarkedForExecution,
    PresidentialPardon,
    PresidentialPolicyPeek,
    PresidentialPropaganda,
)
from src.game.powers.enabling_act_powers import (
    ChancellorExecution,
    ChancellorImpeachment,
    ChancellorMarkedForExecution,
    ChancellorPolicyPeek,
    ChancellorPropaganda,
    VoteOfNoConfidence,
)
from src.game.powers.power_registry import PowerRegistry


@given("que existe una instancia del juego")
def step_given_game_instance(context):
    """Crear una instancia mock del juego para las pruebas"""
    context.game = Mock()
    context.game.name = "Test Game"


@when('solicito el poder "{power_name}"')
def step_when_request_power(context, power_name):
    """Solicitar un poder específico del registry"""
    try:
        context.power_result = PowerRegistry.get_power(power_name, context.game)
        context.error = None
    except Exception as e:
        context.error = e
        context.power_result = None


@then("debería recibir una instancia de {expected_class}")
def step_then_should_receive_instance(context, expected_class):
    """Verificar que se reciba la instancia correcta del poder"""
    assert context.error is None, f"Se produjo un error inesperado: {context.error}"

    # Mapeo de nombres de clases a las clases reales
    class_mapping = {
        "InvestigateLoyalty": InvestigateLoyalty,
        "Confession": Confession,
        "PresidentialPropaganda": PresidentialPropaganda,
        "ChancellorPropaganda": ChancellorPropaganda,
        "SpecialElection": SpecialElection,
        "PolicyPeek": PolicyPeek,
        "Execution": Execution,
        "Bugging": Bugging,
        "FiveYearPlan": FiveYearPlan,
        "Congress": Congress,
        "Radicalization": Radicalization,
    }

    expected_class_obj = class_mapping.get(expected_class)
    assert (
        expected_class_obj is not None
    ), f"Clase no encontrada en el mapeo: {expected_class}"
    assert isinstance(
        context.power_result, expected_class_obj
    ), f"Esperaba {expected_class}, pero recibí {type(context.power_result).__name__}"


@then("el poder debería estar asociado al juego")
def step_then_power_associated_with_game(context):
    """Verificar que el poder esté asociado con la instancia del juego"""
    assert hasattr(context.power_result, "game"), "El poder no tiene atributo 'game'"
    assert (
        context.power_result.game == context.game
    ), "El poder no está asociado con la instancia correcta del juego"


@then("debería recibir un ValueError")
def step_then_should_receive_value_error(context):
    """Verificar que se lance un ValueError"""
    assert context.error is not None, "Se esperaba un error pero no se produjo ninguno"
    assert isinstance(
        context.error, ValueError
    ), f"Se esperaba ValueError, pero se recibió {type(context.error).__name__}"


@then('el mensaje de error debería contener "{expected_message}"')
def step_then_error_message_should_contain(context, expected_message):
    """Verificar que el mensaje de error contenga el texto esperado"""
    assert context.error is not None, "No hay error para verificar el mensaje"
    assert expected_message in str(
        context.error
    ), f"Mensaje de error '{str(context.error)}' no contiene '{expected_message}'"


@when('consulto el propietario del poder "{power_name}"')
def step_when_query_power_owner(context, power_name):
    """Consultar el propietario de un poder específico"""
    context.power_owner = PowerRegistry.get_owner(power_name)


@then("el propietario debería ser {expected_owner}")
def step_then_owner_should_be(context, expected_owner):
    """Verificar que el propietario sea el esperado"""
    expected_owner_enum = getattr(PowerOwner, expected_owner)
    assert (
        context.power_owner == expected_owner_enum
    ), f"Esperaba {expected_owner}, pero recibí {context.power_owner}"


@when("solicito un poder aleatorio del Artículo 48")
def step_when_request_article48_power(context):
    """Solicitar un poder aleatorio del Artículo 48"""
    context.article48_power = PowerRegistry.get_article48_power()


@then("debería recibir un poder válido del Artículo 48")
def step_then_should_receive_valid_article48_power(context):
    """Verificar que el poder del Artículo 48 sea válido"""
    valid_article48_powers = [
        "propaganda",
        "impeachment",
        "marked_for_execution",
        "policy_peek_emergency",
        "execution_emergency",
        "pardon",
    ]
    assert (
        context.article48_power in valid_article48_powers
    ), f"Poder '{context.article48_power}' no es un poder válido del Artículo 48"


@then("el poder debería estar en la lista de poderes presidenciales de emergencia")
def step_then_power_in_presidential_emergency_list(context):
    """Verificar que el poder esté en la lista de poderes presidenciales de emergencia"""
    # Esta verificación es redundante con el step anterior, pero mantenemos la semántica
    valid_powers = [
        "propaganda",
        "impeachment",
        "marked_for_execution",
        "policy_peek_emergency",
        "execution_emergency",
        "pardon",
    ]
    assert context.article48_power in valid_powers


@when("solicito un poder aleatorio del Acta Habilitante")
def step_when_request_enabling_act_power(context):
    """Solicitar un poder aleatorio del Acta Habilitante"""
    context.enabling_act_power = PowerRegistry.get_enabling_act_power()


@then("debería recibir un poder válido del Acta Habilitante")
def step_then_should_receive_valid_enabling_act_power(context):
    """Verificar que el poder del Acta Habilitante sea válido"""
    valid_enabling_act_powers = [
        "chancellor_propaganda",
        "chancellor_impeachment",
        "chancellor_marked_for_execution",
        "chancellor_policy_peek",
        "chancellor_execution",
        "vote_of_no_confidence",
    ]
    assert (
        context.enabling_act_power in valid_enabling_act_powers
    ), f"Poder '{context.enabling_act_power}' no es un poder válido del Acta Habilitante"


@then("el poder debería estar en la lista de poderes del canciller de emergencia")
def step_then_power_in_chancellor_emergency_list(context):
    """Verificar que el poder esté en la lista de poderes del canciller de emergencia"""
    valid_powers = [
        "chancellor_propaganda",
        "chancellor_impeachment",
        "chancellor_marked_for_execution",
        "chancellor_policy_peek",
        "chancellor_execution",
        "vote_of_no_confidence",
    ]
    assert context.enabling_act_power in valid_powers


@when("obtengo todos los poderes fascistas disponibles")
def step_when_get_all_fascist_powers(context):
    """Obtener todos los poderes fascistas para verificación"""
    context.fascist_powers = [
        "investigate_loyalty",
        "special_election",
        "policy_peek",
        "execution",
    ]


@then("todos los poderes fascistas deberían ser instanciables")
def step_then_all_fascist_powers_instantiable(context):
    """Verificar que todos los poderes fascistas se puedan instanciar"""
    for power_name in context.fascist_powers:
        try:
            power_instance = PowerRegistry.get_power(power_name, context.game)
            assert (
                power_instance is not None
            ), f"No se pudo instanciar el poder: {power_name}"
        except Exception as e:
            assert False, f"Error al instanciar el poder {power_name}: {e}"


@then("cada poder debería tener un propietario válido")
def step_then_each_power_has_valid_owner(context):
    """Verificar que cada poder tenga un propietario válido"""
    for power_name in context.fascist_powers:
        owner = PowerRegistry.get_owner(power_name)
        assert isinstance(
            owner, PowerOwner
        ), f"El propietario del poder {power_name} no es una instancia válida de PowerOwner"


@when("solicito múltiples poderes del Artículo 48")
def step_when_request_multiple_article48_powers(context):
    """Solicitar múltiples poderes del Artículo 48 para verificar consistencia"""
    context.multiple_article48_powers = [
        PowerRegistry.get_article48_power() for _ in range(3)
    ]


@then('todos deberían devolver "{expected_power}"')
def step_then_all_should_return_specific_power(context, expected_power):
    """Verificar que todos los poderes devueltos sean el esperado (comportamiento hardcodeado)"""
    # Determinar qué tipo de poderes verificar basado en el expected_power
    if expected_power == "policy_peek_emergency":
        # Verificar poderes del Artículo 48
        assert hasattr(
            context, "multiple_article48_powers"
        ), "No se han solicitado múltiples poderes del Artículo 48"
        for power in context.multiple_article48_powers:
            assert (
                power == expected_power
            ), f"Esperaba '{expected_power}', pero recibí '{power}'"

    elif expected_power == "vote_of_no_confidence":
        # Verificar poderes del Acta Habilitante
        assert hasattr(
            context, "multiple_enabling_act_powers"
        ), "No se han solicitado múltiples poderes del Acta Habilitante"
        for power in context.multiple_enabling_act_powers:
            assert (
                power == expected_power
            ), f"Esperaba '{expected_power}', pero recibí '{power}'"

    else:
        # Para otros casos, verificar ambos si existen
        found_match = False
        if hasattr(context, "multiple_article48_powers"):
            for power in context.multiple_article48_powers:
                if power == expected_power:
                    found_match = True
                    break

        if not found_match and hasattr(context, "multiple_enabling_act_powers"):
            for power in context.multiple_enabling_act_powers:
                assert (
                    power == expected_power
                ), f"Esperaba '{expected_power}', pero recibí '{power}'"


@when("solicito múltiples poderes del Acta Habilitante")
def step_when_request_multiple_enabling_act_powers(context):
    """Solicitar múltiples poderes del Acta Habilitante para verificar consistencia"""
    context.multiple_enabling_act_powers = [
        PowerRegistry.get_enabling_act_power() for _ in range(3)
    ]
