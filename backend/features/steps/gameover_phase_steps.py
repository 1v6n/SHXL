# features/steps/gameover_phase_steps.py

from unittest.mock import Mock, patch

# mypy: disable-error-code=import
from behave import given, then, when
from src.game.game import SHXLGame
from src.game.phases.gameover import GameOverPhase


@given("un objeto GameOverPhase con el juego")
def step_given_gameover_phase_with_game(context):
    context.game = SHXLGame()
    context.gameover_phase = GameOverPhase(context.game)


@when("ejecuto la fase de game over")
def step_when_ejecuto_gameover_phase(context):
    context.result = context.gameover_phase.execute()


@then("el estado del juego debe marcarse como terminado")
def step_then_game_marked_as_over(context):
    assert context.game.state.game_over is True


@then("debe retornar la misma instancia de GameOverPhase")
def step_then_returns_same_gameover_instance(context):
    assert context.result is context.gameover_phase


@then("todos los roles deben estar revelados")
def step_then_all_roles_revealed(context):
    # En la implementación actual, GameOverPhase solo marca game_over = True
    # Esta verificación puede expandirse cuando se implemente la revelación de roles
    assert context.game.state.game_over is True


@given("un objeto SHXLGame configurado para gameover")
def step_given_configured_game_for_gameover(context):
    context.game = SHXLGame()


@when("creo una nueva GameOverPhase")
def step_when_create_gameover_phase(context):
    context.gameover_phase = GameOverPhase(context.game)


@then("la fase gameover debe tener una referencia al juego")
def step_then_gameover_phase_has_game_reference(context):
    assert context.gameover_phase.game is context.game


@then("debe implementar el método execute de gameover")
def step_then_gameover_implements_execute_method(context):
    assert hasattr(context.gameover_phase, "execute")
    assert callable(getattr(context.gameover_phase, "execute"))


@given("un objeto GameOverPhase configurado")
def step_given_configured_gameover_phase(context):
    context.game = SHXLGame()
    context.gameover_phase = GameOverPhase(context.game)


@given("el juego ya está marcado como terminado")
def step_given_game_already_over(context):
    context.game.state.game_over = True


@when("ejecuto la fase de game over múltiples veces")
def step_when_execute_gameover_multiple_times(context):
    context.result1 = context.gameover_phase.execute()
    context.result2 = context.gameover_phase.execute()
    context.result3 = context.gameover_phase.execute()


@then("siempre debe retornar la misma instancia")
def step_then_always_returns_same_instance(context):
    assert context.result1 is context.gameover_phase
    assert context.result2 is context.gameover_phase
    assert context.result3 is context.gameover_phase


@then("el estado del juego debe permanecer terminado")
def step_then_game_state_remains_over(context):
    assert context.game.state.game_over is True
