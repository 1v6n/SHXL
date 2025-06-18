from collections import Counter

# mypy: disable-error-code=import
from behave import given, then, when
from src.policies.policy_factory import PolicyFactory


@given("una partida de {player_count:d} jugadores")
def step_impl_players(context, player_count):
    context.player_count = player_count


@given("la opción comunistas está {status}")
def step_impl_communists(context, status):
    context.with_communists = status.lower() == "true"


@given("la opción anti-policies está {status}")
def step_impl_antipolicies(context, status):
    context.with_anti_policies = status.lower() == "true"


@given("la opción poderes de emergencia está {status}")
def step_impl_emergency(context, status):
    context.with_emergency_powers = status.lower() == "true"


@when("genero el mazo de políticas")
def step_impl_generate_deck(context):
    context.deck = PolicyFactory.create_policy_deck(
        context.player_count,
        with_communists=context.with_communists,
        with_anti_policies=context.with_anti_policies,
        with_emergency_powers=context.with_emergency_powers,
    )
    context.counts = Counter([card.type for card in context.deck])


@then("el mazo debe contener {count:d} cartas {card_type}")
@then("{count:d} cartas {card_type}")
def step_impl_card_count(context, count, card_type):
    type_map = {
        "liberales": "liberal",
        "fascistas": "fascist",
        "comunistas": "communist",
        "anti-fascistas": "antifascist",
        "anti-comunistas": "anticommunist",
        "socialdemócratas": "socialdemocratic",
        "Article 48": "article48",
        "Enabling Act": "enablingact",
    }
    # Normaliza el nombre para buscarlo en el Counter
    normalized_type = type_map.get(card_type.strip(), card_type.strip().lower())
    cantidad = context.counts.get(normalized_type, 0)
    assert (
        cantidad == count
    ), f"Esperaba {count} cartas '{card_type}', pero encontré {cantidad}"
