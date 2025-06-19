# features/steps/setup_phase_steps.py

from unittest.mock import Mock, patch

# mypy: disable-error-code=import
from behave import given, then, when
from src.game.game import SHXLGame
from src.game.phases.election import ElectionPhase
from src.game.phases.setup import SetupPhase


@given("un objeto SetupPhase con el juego")
def step_given_setup_phase_with_game(context):
    context.game = SHXLGame()
    context.setup_phase = SetupPhase(context.game)


@when("ejecuto la fase de configuración")
def step_when_ejecuto_setup_phase(context):
    context.result = context.setup_phase.execute()


@then("debe retornar una instancia de ElectionPhase")
def step_then_returns_election_phase(context):
    assert isinstance(context.result, ElectionPhase)


@then("el resultado debe ser una ElectionPhase con referencia al juego")
def step_then_result_is_election_phase_with_game(context):
    assert isinstance(context.result, ElectionPhase)
    assert context.result.game is context.game


@given("un objeto SHXLGame configurado para setup")
def step_given_configured_game(context):
    context.game = SHXLGame()


@when("creo una nueva SetupPhase")
def step_when_create_setup_phase(context):
    context.setup_phase = SetupPhase(context.game)


@then("la fase setup debe tener una referencia al juego")
def step_then_phase_has_game_reference(context):
    assert context.setup_phase.game is context.game


@then("debe implementar el método execute de setup")
def step_then_implements_execute_method(context):
    assert hasattr(context.setup_phase, "execute")
    assert callable(getattr(context.setup_phase, "execute"))
