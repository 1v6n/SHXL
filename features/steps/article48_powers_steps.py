from unittest.mock import MagicMock, Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.game.powers.article48_powers import (
    PowerOwner,
    PresidentialExecution,
    PresidentialImpeachment,
    PresidentialMarkedForExecution,
    PresidentialPardon,
    PresidentialPolicyPeek,
    PresidentialPropaganda,
)


@given('que existe un juego con políticas en el mazo')
def juego_con_politicas(context):
    """Configura un juego mock con políticas disponibles"""
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.board = Mock()
    context.game.state.board.policies = ['liberal', 'fascist', 'liberal']
    context.game.state.board.discard = Mock()
    context.game.state.president = Mock()
    context.game.state.president.propaganda_decision = Mock(return_value=True)
    context.game.logger = Mock()
    # Configurar el comportamiento del mock para el descarte
    context.discard_mock = Mock()
    context.game.state.board.discard = context.discard_mock


@given('que existe un juego sin políticas en el mazo')
def juego_sin_politicas(context):
    """Configura un juego mock sin políticas disponibles"""
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.board = Mock()
    context.game.state.board.policies = []
    context.game.logger = Mock()


@given('que existe un juego con al menos 3 políticas en el mazo')
def juego_con_3_politicas(context):
    """Configura un juego mock con al menos 3 políticas"""
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.board = Mock()
    context.game.state.board.policies = ['liberal', 'fascist', 'liberal', 'fascist']


@given('que existe un juego con 2 políticas en el mazo')
def juego_con_2_politicas(context):
    """Configura un juego mock con exactamente 2 políticas"""
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.board = Mock()
    context.game.state.board.policies = ['liberal', 'fascist']


@given('que existe un juego con jugadores activos')
def juego_con_jugadores_activos(context):
    """Configura un juego mock con jugadores activos"""
    context.game = Mock()
    context.game.state = Mock()
    context.jugador_objetivo = Mock()
    context.jugador_objetivo.is_dead = False
    context.jugador_objetivo.id = "player_1"
    context.jugador_objetivo.name = "Test Player"
    context.game.state.active_players = [context.jugador_objetivo]


@given('que existe un juego activo')
def juego_activo(context):
    """Configura un juego activo básico"""
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.board = Mock()
    context.game.state.board.fascist_track = 2
    context.game.logger = Mock()
    context.jugador_objetivo = Mock()
    context.jugador_objetivo.id = "player_1"
    context.jugador_objetivo.name = "Test Player"


@given('que existe un juego con un jugador marcado para ejecución')
def juego_con_jugador_marcado(context):
    """Configura un juego con un jugador ya marcado para ejecución"""
    context.game = Mock()
    context.game.state = Mock()
    context.jugador_marcado = Mock()
    context.jugador_marcado.id = "marked_player"
    context.jugador_marcado.name = "Marked Player"
    context.game.state.marked_for_execution = context.jugador_marcado
    context.game.state.marked_for_execution_tracker = 3
    context.game.logger = Mock()


@given('que existe un juego sin jugadores marcados para ejecución')
def juego_sin_jugadores_marcados(context):
    """Configura un juego sin jugadores marcados para ejecución"""
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.marked_for_execution = None
    context.game.logger = Mock()


@given('que existe un juego con al menos 3 jugadores activos')
def juego_con_3_jugadores(context):
    """Configura un juego con al menos 3 jugadores activos"""
    context.game = Mock()
    context.game.state = Mock()

    context.presidente = Mock()
    context.presidente.id = "president"
    context.canciller = Mock()
    context.canciller.id = "chancellor"
    context.canciller.role = Mock()
    context.canciller.role.party_membership = "liberal"
    context.otro_jugador = Mock()
    context.otro_jugador.id = "other_player"
    context.otro_jugador.known_affiliations = {}

    context.game.state.president = context.presidente
    context.game.state.active_players = [context.presidente, context.canciller, context.otro_jugador]
    context.game.state.president.choose_revealer = Mock(return_value=context.otro_jugador)


@given('que existe un juego con solo el presidente y canciller activos')
def juego_solo_presidente_canciller(context):
    """Configura un juego con solo presidente y canciller"""
    context.game = Mock()
    context.game.state = Mock()

    context.presidente = Mock()
    context.presidente.id = "president"
    context.canciller = Mock()
    context.canciller.id = "chancellor"

    context.game.state.president = context.presidente
    context.game.state.active_players = [context.presidente, context.canciller]


@given('el presidente tiene el poder de propaganda')
def poder_propaganda(context):
    """Crea una instancia del poder de propaganda"""
    # Crear la instancia real del poder, no un mock
    context.poder = PresidentialPropaganda(context.game)


@given('el presidente tiene el poder de espionaje de políticas')
def poder_espionaje(context):
    """Crea una instancia del poder de espionaje de políticas"""
    context.poder = PresidentialPolicyPeek(context.game)


@given('el presidente tiene el poder de ejecución')
def poder_ejecucion(context):
    """Crea una instancia del poder de ejecución"""
    context.poder = PresidentialExecution(context.game)


@given('el presidente tiene el poder de marcar para ejecución')
def poder_marcar_ejecucion(context):
    """Crea una instancia del poder de marcar para ejecución"""
    context.poder = PresidentialMarkedForExecution(context.game)


@given('el presidente tiene el poder de perdón')
def poder_perdon(context):
    """Crea una instancia del poder de perdón"""
    context.poder = PresidentialPardon(context.game)


@given('el presidente tiene el poder de revelación')
def poder_revelacion(context):
    """Crea una instancia del poder de revelación"""
    context.poder = PresidentialImpeachment(context.game)


@given('existe un jugador objetivo vivo')
def jugador_objetivo_vivo(context):
    """Establece que existe un jugador objetivo vivo"""
    pass  # Ya configurado en juego_con_jugadores_activos


@given('existe un jugador objetivo')
def jugador_objetivo_existe(context):
    """Establece que existe un jugador objetivo"""
    pass  # Ya configurado en juego_activo


@given('existe un canciller objetivo')
def canciller_objetivo(context):
    """Establece que existe un canciller objetivo"""
    pass  # Ya configurado en juego_con_3_jugadores


@when('el presidente ejecuta el poder de propaganda')
def ejecutar_propaganda(context):
    """Ejecuta el poder de propaganda"""
    context.politicas_originales = len(context.game.state.board.policies)
    context.resultado = context.poder.execute()


@when('decide descartar la política vista')
def decidir_descartar(context):
    """Configura la decisión de descartar"""
    context.game.state.president.propaganda_decision.return_value = True


@when('decide no descartar la política vista')
def decidir_no_descartar(context):
    """Configura la decisión de no descartar"""
    context.game.state.president.propaganda_decision.return_value = False


@when('el presidente ejecuta el poder de espionaje')
def ejecutar_espionaje(context):
    """Ejecuta el poder de espionaje de políticas"""
    context.resultado = context.poder.execute()


@when('el presidente ejecuta el poder de ejecución contra el jugador objetivo')
def ejecutar_ejecucion(context):
    """Ejecuta el poder de ejecución"""
    context.resultado = context.poder.execute(context.jugador_objetivo)


@when('el presidente marca al jugador objetivo para ejecución')
def marcar_para_ejecucion(context):
    """Ejecuta el poder de marcar para ejecución"""
    context.resultado = context.poder.execute(context.jugador_objetivo)


@when('el presidente ejecuta el poder de perdón')
def ejecutar_perdon(context):
    """Ejecuta el poder de perdón"""
    context.resultado = context.poder.execute()


@when('el presidente ejecuta el poder de revelación contra el canciller')
def ejecutar_revelacion(context):
    """Ejecuta el poder de revelación"""
    context.resultado = context.poder.execute(context.canciller)


@when('selecciona un jugador revelador válido')
def seleccionar_revelador(context):
    """Configura la selección de jugador revelador"""
    pass  # Ya configurado en el mock


@when('el presidente intenta ejecutar el poder de revelación')
def intentar_revelacion(context):
    """Intenta ejecutar el poder de revelación"""
    context.resultado = context.poder.execute(context.canciller)


@then('la política debe ser removida del mazo')
def politica_removida_mazo(context):
    """Verifica que la política fue removida del mazo"""
    politicas_actuales = len(context.game.state.board.policies)
    assert politicas_actuales == context.politicas_originales - 1, \
        f"Esperaba {context.politicas_originales - 1} políticas, pero hay {politicas_actuales}"


@then('la política debe ser añadida a la pila de descarte')
def politica_en_descarte(context):
    """Verifica que la política fue descartada"""
    # Verificar que el método discard fue llamado en el board
    context.game.state.board.discard.assert_called_once()


@then('la política debe permanecer en el mazo')
def politica_permanece_mazo(context):
    """Verifica que la política permanece en el mazo"""
    politicas_actuales = len(context.game.state.board.policies)
    assert politicas_actuales == context.politicas_originales, \
        f"Esperaba {context.politicas_originales} políticas, pero hay {politicas_actuales}"


@then('la pila de descarte no debe cambiar')
def descarte_sin_cambios(context):
    """Verifica que no se descartó nada"""
    context.game.state.board.discard.assert_not_called()


@then('el poder debe retornar None')
def poder_retorna_none(context):
    """Verifica que el resultado es None"""
    assert context.resultado is None, f"Esperaba None, pero obtuvo {context.resultado}"


@then('no debe ocurrir ningún cambio en el estado del juego')
def sin_cambios_estado(context):
    """Verifica que no hubo cambios en el estado"""
    # Verificar que las políticas no cambiaron
    assert len(context.game.state.board.policies) == 0, \
        "No debería haber políticas en el mazo vacío"


@then('debe poder ver las primeras 3 políticas')
def ver_3_politicas(context):
    """Verifica que se pueden ver las primeras 3 políticas"""
    assert len(context.resultado) == 3
    assert context.resultado == ['liberal', 'fascist', 'liberal']


@then('las políticas no deben ser removidas del mazo')
def politicas_no_removidas(context):
    """Verifica que las políticas siguen en el mazo"""
    assert len(context.game.state.board.policies) == 4  # Sin cambios


@then('debe retornar solo las 2 políticas disponibles')
def retorna_2_politicas(context):
    """Verifica que retorna solo las políticas disponibles"""
    assert len(context.resultado) == 2
    assert context.resultado == ['liberal', 'fascist']


@then('el jugador objetivo debe estar marcado como muerto')
def jugador_muerto(context):
    """Verifica que el jugador está marcado como muerto"""
    assert context.jugador_objetivo.is_dead is True


@then('el jugador objetivo debe ser removido de los jugadores activos')
def jugador_removido_activos(context):
    """Verifica que el jugador fue removido de activos"""
    assert context.jugador_objetivo not in context.game.state.active_players


@then('el jugador debe quedar marcado para ejecución')
def jugador_marcado_ejecucion(context):
    """Verifica que el jugador está marcado para ejecución"""
    assert context.game.state.marked_for_execution == context.jugador_objetivo


@then('el contador fascista actual debe ser registrado')
def contador_fascista_registrado(context):
    """Verifica que se registró el contador fascista"""
    assert context.game.state.marked_for_execution_tracker == 2


@then('el jugador marcado debe ser liberado')
def jugador_liberado(context):
    """Verifica que el jugador marcado fue liberado"""
    assert context.game.state.marked_for_execution is None


@then('la marca de ejecución debe ser eliminada')
def marca_eliminada(context):
    """Verifica que la marca de ejecución fue eliminada"""
    assert context.game.state.marked_for_execution_tracker is None


@then('debe registrar que no hay jugador marcado')
def registra_sin_jugador_marcado(context):
    """Verifica que se registró la ausencia de jugador marcado"""
    context.game.logger.log.assert_called_with("No player is currently marked for execution.")


@then('el jugador revelador debe conocer el partido del canciller')
def revelador_conoce_partido(context):
    """Verifica que el revelador conoce el partido del canciller"""
    assert hasattr(context.otro_jugador, 'known_affiliations')
    assert context.otro_jugador.known_affiliations[context.canciller.id] == "liberal"


@then('la información debe ser almacenada correctamente')
def informacion_almacenada(context):
    """Verifica que la información se almacenó correctamente"""
    assert context.resultado is True


@then('el poder debe retornar False')
def poder_retorna_false(context):
    """Verifica que el resultado es False"""
    assert context.resultado is False


@then('no debe ocurrir revelación alguna')
def sin_revelacion(context):
    """Verifica que no ocurrió revelación"""
    pass  # Verificación implícita por el False retornado
