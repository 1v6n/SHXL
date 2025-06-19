from collections import Counter

# mypy: disable-error-code=import
from behave import then, when
from src.roles.role_factory import RoleFactory

# Note: The step "una partida de {player_count:d} jugadores" is already defined in policy_deck_steps.py
# Note: The step "la opción comunistas está {status}" is already defined in policy_deck_steps.py


@when("genero los roles")
def step_impl_generate_roles(context):
    """Generate roles using RoleFactory and count them by type."""
    context.roles = RoleFactory.create_roles(
        context.player_count, with_communists=context.with_communists
    )
    context.role_counts = Counter([role.role for role in context.roles])


@then("la distribución debe contener {count:d} roles {role_type}")
@then("{count:d} roles {role_type}")
def step_impl_role_count(context, count, role_type):
    """Verify that the generated roles contain the expected count of each type."""
    type_map = {
        "liberales": "liberal",
        "fascistas": "fascist",
        "comunistas": "communist",
        "Hitler": "hitler",
    }
    # Normalize the role type name
    normalized_type = type_map.get(role_type.strip(), role_type.strip().lower())
    actual_count = context.role_counts.get(normalized_type, 0)
    assert (
        actual_count == count
    ), f"Esperaba {count} roles '{role_type}', pero encontré {actual_count}"


@then("el total de roles debe ser {expected_total:d}")
def step_impl_total_roles(context, expected_total):
    """Verify that the total number of roles matches the player count."""
    actual_total = len(context.roles)
    assert (
        actual_total == expected_total
    ), f"Esperaba {expected_total} roles en total, pero encontré {actual_total}"
