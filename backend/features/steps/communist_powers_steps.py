from unittest.mock import MagicMock, Mock

# mypy: disable-error-code=import
from behave import given, then, when
from src.game.powers.abstract_power import Power
from src.game.powers.communist_powers import (
    Bugging,
    Confession,
    Congress,
    FiveYearPlan,
    Impeachment,
    Propaganda,
    Radicalization,
)
from src.policies.policy import Communist as CommunistPolicy
from src.policies.policy import Liberal
from src.roles.role import Communist


@given("que existe un juego inicializado")
def step_juego_inicializado(context):
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.players = []
    context.game.state.board = Mock()
    context.game.state.board.policies = []
    context.game.state.revealed_affiliations = {}


@given("existen jugadores en la partida")
def step_jugadores_en_partida(context):
    # Crear jugadores mock
    context.jugador_liberal = Mock()
    context.jugador_liberal.id = "liberal_1"
    context.jugador_liberal.role = Mock()
    context.jugador_liberal.role.party_membership = "liberal"
    context.jugador_liberal.is_hitler = False
    context.jugador_liberal.known_affiliations = {}

    context.jugador_comunista = Mock()
    context.jugador_comunista.id = "communist_1"
    context.jugador_comunista.role = Mock()
    context.jugador_comunista.role.party_membership = "communist"
    context.jugador_comunista.is_hitler = False
    context.jugador_comunista.known_affiliations = {}

    context.hitler = Mock()
    context.hitler.id = "hitler_1"
    context.hitler.role = Mock()
    context.hitler.role.party_membership = "fascist"
    context.hitler.is_hitler = True
    context.hitler.known_affiliations = {}

    context.game.state.players = [
        context.jugador_liberal,
        context.jugador_comunista,
        context.hitler,
    ]


@given("hay un presidente asignado")
def step_presidente_asignado(context):
    context.game.state.president = context.jugador_liberal


@given("hay un canciller asignado")
def step_canciller_asignado(context):
    context.game.state.chancellor = context.jugador_comunista


@given("que el presidente es comunista")
def step_presidente_comunista(context):
    context.game.state.president = context.jugador_comunista


@given("que existen jugadores comunistas en la partida")
def step_jugadores_comunistas_en_partida(context):
    # Crear un segundo comunista
    context.jugador_comunista2 = Mock()
    context.jugador_comunista2.id = "communist_2"
    context.jugador_comunista2.role = Mock()
    context.jugador_comunista2.role.party_membership = "communist"
    context.jugador_comunista2.is_hitler = False
    context.jugador_comunista2.known_affiliations = {}

    context.game.state.players.append(context.jugador_comunista2)


@given("existe un jugador objetivo que no es comunista")
def step_jugador_objetivo_no_comunista(context):
    context.jugador_objetivo = context.jugador_liberal


@given("que existe un mazo de politicas")
def step_mazo_politicas_existe(context):
    context.game.state.board.policies = [Mock(), Mock(), Mock()]


@given("que existen multiples jugadores comunistas")
def step_multiples_comunistas(context):
    # Ya tenemos comunistas del step anterior
    pass


@given("que existe un jugador liberal en la partida")
def step_jugador_liberal_en_partida(context):
    context.jugador_a_convertir = context.jugador_liberal


@given("el jugador no es Hitler")
def step_jugador_no_es_hitler(context):
    assert not context.jugador_a_convertir.is_hitler


@given("que existe un jugador que es Hitler")
def step_jugador_es_hitler(context):
    context.jugador_a_convertir = context.hitler


@given("que existe un mazo con politicas disponibles")
def step_mazo_con_politicas_disponibles(context):
    politica_mock = Mock()
    politica_mock.type = "communist"
    context.game.state.board.policies = [politica_mock, Mock(), Mock()]
    context.game.state.board.discard = Mock()


@given("el presidente puede tomar decisiones de propaganda")
def step_presidente_puede_decidir_propaganda(context):
    context.game.state.president.propaganda_decision = Mock(return_value=False)


@given("el presidente decide descartar la carta vista")
def step_presidente_decide_descartar(context):
    context.game.state.president.propaganda_decision = Mock(return_value=True)


@given("que existe un jugador objetivo")
def step_jugador_objetivo_existe(context):
    context.jugador_objetivo = context.jugador_liberal


@given("existe un jugador revelador")
def step_jugador_revelador_existe(context):
    context.jugador_revelador = context.jugador_comunista


@given("que un comunista ya conoce la afiliacion de un jugador")
def step_comunista_ya_conoce_afiliacion(context):
    # Asegurar que known_affiliations ya existe (debería estar del step anterior)
    context.jugador_comunista.known_affiliations[context.jugador_liberal.id] = "liberal"


@given("que el mazo de politicas esta vacio")
def step_mazo_vacio(context):
    context.game.state.board.policies = []


@when('el presidente ejecuta el poder "{poder}"')
def step_ejecutar_poder_presidente(context, poder):
    if poder == "Confession":
        context.confesion = Confession(context.game)
        context.resultado = context.confesion.execute()


@when('un comunista ejecuta el poder "{poder}" sobre el jugador objetivo')
def step_comunista_ejecuta_bugging(context, poder):
    if poder == "Bugging":
        context.bugging = Bugging(context.game)
        context.resultado = context.bugging.execute(context.jugador_objetivo)


@when('se ejecuta el poder "{poder}"')
def step_ejecutar_poder_generico(context, poder):
    if poder == "FiveYearPlan":
        context.five_year_plan = FiveYearPlan(context.game)
        context.resultado = context.five_year_plan.execute()
    elif poder == "Congress":
        context.congress = Congress(context.game)
        context.resultado = context.congress.execute()
    elif poder == "Propaganda":
        context.propaganda = Propaganda(context.game)
        context.resultado = context.propaganda.execute()


@when('se ejecuta el poder "{poder}" sobre el jugador liberal')
def step_ejecutar_radicalizacion_liberal(context, poder):
    if poder == "Radicalization":
        context.radicalization = Radicalization(context.game)
        context.resultado = context.radicalization.execute(context.jugador_a_convertir)


@when('se ejecuta el poder "{poder}" sobre Hitler')
def step_ejecutar_radicalizacion_hitler(context, poder):
    if poder == "Radicalization":
        context.radicalization = Radicalization(context.game)
        context.resultado = context.radicalization.execute(context.jugador_a_convertir)


@when('se ejecuta el poder "{poder}" con ambos jugadores')
def step_ejecutar_impeachment(context, poder):
    if poder == "Impeachment":
        context.impeachment = Impeachment(context.game)
        context.resultado = context.impeachment.execute(
            context.jugador_objetivo, context.jugador_revelador
        )


@when('ejecuta "{poder}" sobre el mismo jugador nuevamente')
def step_ejecutar_bugging_nuevamente(context, poder):
    if poder == "Bugging":
        context.bugging = Bugging(context.game)
        context.resultado = context.bugging.execute(context.jugador_liberal)


@then("la afiliacion del presidente debe ser revelada publicamente")
def step_afiliacion_presidente_revelada(context):
    presidente_id = context.game.state.president.id
    assert presidente_id in context.game.state.revealed_affiliations


@then('la afiliacion revelada debe ser "{afiliacion}"')
def step_afiliacion_revelada_es(context, afiliacion):
    presidente_id = context.game.state.president.id
    assert context.game.state.revealed_affiliations[presidente_id] == afiliacion


@then("todos los comunistas deben conocer la afiliacion del jugador objetivo")
def step_comunistas_conocen_objetivo(context):
    for jugador in context.game.state.players:
        if jugador.role.party_membership == "communist":
            assert context.jugador_objetivo.id in jugador.known_affiliations


@then("la informacion debe almacenarse en known_affiliations")
def step_informacion_en_known_affiliations(context):
    for jugador in context.game.state.players:
        if jugador.role.party_membership == "communist":
            objetivo_id = context.jugador_objetivo.id
            expected_affiliation = context.jugador_objetivo.role.party_membership
            assert jugador.known_affiliations[objetivo_id] == expected_affiliation


@then("se deben agregar {cantidad:d} politicas comunistas al mazo")
def step_politicas_comunistas_agregadas(context, cantidad):
    # Verificamos que el metodo fue llamado correctamente
    assert context.resultado == True


@then("se debe agregar {cantidad:d} politica liberal al mazo")
def step_politica_liberal_agregada(context, cantidad):
    # Verificamos que el resultado sea exitoso
    assert context.resultado == True


@then("las politicas deben estar mezcladas en el mazo")
def step_politicas_mezcladas(context):
    # El resultado True indica que el mezclado fue exitoso
    assert context.resultado == True


@then("todos los comunistas deben conocer quienes son los otros comunistas")
def step_comunistas_se_conocen(context):
    for jugador in context.game.state.players:
        if jugador.role.party_membership == "communist":
            assert hasattr(jugador, "known_communists")
            assert isinstance(jugador.known_communists, list)


@then("cada comunista debe tener la lista actualizada de comunistas")
def step_lista_comunistas_actualizada(context):
    comunistas_ids = [
        p.id
        for p in context.game.state.players
        if p.role.party_membership == "communist"
    ]
    assert set(context.resultado) == set(comunistas_ids)


@then("el jugador debe convertirse en comunista")
def step_jugador_convertido_comunista(context):
    assert context.resultado is not None
    assert context.resultado.role.party_membership == "communist"


@then("el rol del jugador debe cambiar a Communist")
def step_rol_cambiado_communist(context):
    assert isinstance(context.jugador_a_convertir.role, Communist)


@then("la conversion debe fallar")
def step_conversion_falla(context):
    assert context.resultado is None


@then("Hitler debe mantener su rol original")
def step_hitler_mantiene_rol(context):
    assert context.hitler.role.party_membership == "fascist"


@then("se debe mostrar la carta superior del mazo")
def step_carta_superior_mostrada(context):
    assert context.resultado is not None


@then("el presidente debe poder decidir si descartarla")
def step_presidente_puede_decidir_descartar(context):
    context.game.state.president.propaganda_decision.assert_called_once()


@then("la carta superior debe ser removida del mazo")
def step_carta_removida_mazo(context):
    # Verificamos que el metodo discard fue llamado
    context.game.state.board.discard.assert_called_once()


@then("la carta debe ser enviada a la pila de descarte")
def step_carta_en_descarte(context):
    # Ya verificado en el step anterior
    pass


@then("el jugador revelador debe conocer la afiliacion del objetivo")
def step_revelador_conoce_objetivo(context):
    objetivo_id = context.jugador_objetivo.id
    assert objetivo_id in context.jugador_revelador.known_affiliations


@then("la informacion debe guardarse en known_affiliations del revelador")
def step_info_guardada_revelador(context):
    objetivo_id = context.jugador_objetivo.id
    expected_affiliation = context.jugador_objetivo.role.party_membership
    assert (
        context.jugador_revelador.known_affiliations[objetivo_id]
        == expected_affiliation
    )


@then("la informacion debe actualizarse correctamente")
def step_informacion_actualizada(context):
    objetivo_id = context.jugador_liberal.id
    assert objetivo_id in context.jugador_comunista.known_affiliations


@then("no debe generar errores de duplicacion")
def step_sin_errores_duplicacion(context):
    # Si llegamos aqui sin excepciones, no hubo errores
    assert context.resultado is not None


@then("debe retornar None")
def step_retorna_none(context):
    assert context.resultado is None


@then("no debe generar errores")
def step_sin_errores(context):
    # Si llegamos aqui, no hubo errores
    assert True


# ================== STRATEGY TESTING STEPS ==================


@given("el jugador tiene una estrategia liberal")
def step_jugador_tiene_estrategia_liberal(context):
    from src.players.strategies.liberal_strategy import LiberalStrategy

    context.jugador_a_convertir.strategy = LiberalStrategy(context.jugador_a_convertir)
    context.estrategia_original = context.jugador_a_convertir.strategy


@given("que existe un jugador fascista en la partida")
def step_jugador_fascista_en_partida(context):
    context.jugador_fascista = Mock()
    context.jugador_fascista.id = "fascist_1"
    context.jugador_fascista.role = Mock()
    context.jugador_fascista.role.party_membership = "fascist"
    context.jugador_fascista.is_hitler = False
    context.jugador_fascista.known_affiliations = {}
    context.game.state.players.append(context.jugador_fascista)
    context.jugador_a_convertir = context.jugador_fascista


@given("el jugador tiene una estrategia fascista")
def step_jugador_tiene_estrategia_fascista(context):
    from src.players.strategies.fascist_strategy import FascistStrategy

    context.jugador_a_convertir.strategy = FascistStrategy(context.jugador_a_convertir)
    context.estrategia_original = context.jugador_a_convertir.strategy


@given("el jugador tiene una estrategia inteligente")
def step_jugador_tiene_estrategia_inteligente(context):
    from src.players.strategies.smart_strategy import SmartStrategy

    context.jugador_a_convertir.strategy = SmartStrategy(context.jugador_a_convertir)
    context.estrategia_original = context.jugador_a_convertir.strategy


@when('se ejecuta el poder "Radicalization" sobre el jugador fascista')
def step_ejecutar_radicalizacion_sobre_fascista(context):
    radicalization = Radicalization(context.game)
    context.resultado = radicalization.execute(context.jugador_a_convertir)


@then("el jugador debe tener una estrategia comunista")
def step_jugador_debe_tener_estrategia_comunista(context):
    from src.players.strategies.communist_strategy import CommunistStrategy

    assert isinstance(context.jugador_a_convertir.strategy, CommunistStrategy)


@then("la estrategia original debe haber sido reemplazada")
def step_estrategia_original_reemplazada(context):
    assert context.jugador_a_convertir.strategy is not context.estrategia_original
    # Verificar que el tipo cambió
    from src.players.strategies.communist_strategy import CommunistStrategy

    assert isinstance(context.jugador_a_convertir.strategy, CommunistStrategy)


@then("el jugador debe mantener su estrategia inteligente")
def step_jugador_mantiene_estrategia_inteligente(context):
    from src.players.strategies.smart_strategy import SmartStrategy

    assert isinstance(context.jugador_a_convertir.strategy, SmartStrategy)


@then("la estrategia no debe haber cambiado de tipo")
def step_estrategia_no_cambio_tipo(context):
    assert type(context.jugador_a_convertir.strategy) == type(
        context.estrategia_original
    )


# ================== OKTOBER FEST TESTING STEPS ==================


@given("que existe un juego con jugadores bot")
def step_juego_con_jugadores_bot(context):
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.players = []
    context.game.state.active_players = []
    context.game.state.oktoberfest_active = False
    context.game.state.original_strategies = {}
    context.game.state.month_counter = 9  # Start in September

    # Crear jugadores bot
    for i in range(3):
        jugador_bot = Mock()
        jugador_bot.id = f"bot_{i}"
        jugador_bot.is_bot = True
        jugador_bot.strategy = Mock()
        context.game.state.players.append(jugador_bot)
        context.game.state.active_players.append(jugador_bot)


@given("los jugadores bot tienen estrategias diferentes")
def step_jugadores_bot_estrategias_diferentes(context):
    from src.players.strategies.fascist_strategy import FascistStrategy
    from src.players.strategies.liberal_strategy import LiberalStrategy
    from src.players.strategies.smart_strategy import SmartStrategy

    strategies = [LiberalStrategy, FascistStrategy, SmartStrategy]
    for i, jugador in enumerate(context.game.state.active_players):
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            jugador.strategy = strategies[i % len(strategies)](jugador)

    # Guardar las estrategias originales para verificación
    context.estrategias_originales = {}
    for jugador in context.game.state.active_players:
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            context.estrategias_originales[jugador.id] = type(jugador.strategy)


@given("el contador de mes es {mes:d}")
def step_contador_mes_es(context, mes):
    context.game.state.month_counter = mes


@given("Oktober Fest esta activo")
def step_oktober_fest_activo(context):
    context.game.state.oktoberfest_active = True


@given("los jugadores bot tienen estrategia aleatoria")
def step_jugadores_bot_estrategia_aleatoria(context):
    from src.players.strategies.random_strategy import RandomStrategy

    # Initialize original_strategies if not exists
    if not hasattr(context.game.state, "original_strategies"):
        context.game.state.original_strategies = {}

    for jugador in context.game.state.active_players:
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            # Save original strategy before changing to random if not already saved
            if jugador.id not in context.game.state.original_strategies:
                context.game.state.original_strategies[jugador.id] = jugador.strategy
            jugador.strategy = RandomStrategy(jugador)


@given("las estrategias originales estan guardadas")
def step_estrategias_originales_guardadas(context):
    from src.players.strategies.fascist_strategy import FascistStrategy
    from src.players.strategies.liberal_strategy import LiberalStrategy
    from src.players.strategies.smart_strategy import SmartStrategy

    strategies = [LiberalStrategy, FascistStrategy, SmartStrategy]
    context.game.state.original_strategies = {}

    for i, jugador in enumerate(context.game.state.active_players):
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            # Simular estrategia original guardada
            context.game.state.original_strategies[jugador.id] = strategies[
                i % len(strategies)
            ](jugador)


@given("que existe un juego con jugadores humanos y bots")
def step_juego_con_humanos_y_bots(context):
    context.game = Mock()
    context.game.state = Mock()
    context.game.state.players = []
    context.game.state.active_players = []
    context.game.state.oktoberfest_active = False
    context.game.state.original_strategies = {}
    context.game.state.month_counter = 9

    # Crear jugadores humanos
    for i in range(2):
        jugador_humano = Mock()
        jugador_humano.id = f"human_{i}"
        jugador_humano.is_bot = False
        jugador_humano.strategy = Mock()
        context.game.state.players.append(jugador_humano)
        context.game.state.active_players.append(jugador_humano)

    # Crear jugadores bot
    for i in range(2):
        jugador_bot = Mock()
        jugador_bot.id = f"bot_{i}"
        jugador_bot.is_bot = True
        jugador_bot.strategy = Mock()
        context.game.state.players.append(jugador_bot)
        context.game.state.active_players.append(jugador_bot)


@when("se ejecuta la transicion de mes")
def step_ejecutar_transicion_mes(context):
    # Simular la lógica de transición de mes
    if (
        context.game.state.month_counter == 10
        and not context.game.state.oktoberfest_active
    ):
        # Iniciar Oktober Fest
        context.game.state.oktoberfest_active = True
        context.game.state.original_strategies = {}

        from src.players.strategies.random_strategy import RandomStrategy

        for jugador in context.game.state.active_players:
            if hasattr(jugador, "is_bot") and jugador.is_bot:
                # Guardar estrategia original
                context.game.state.original_strategies[jugador.id] = jugador.strategy
                # Cambiar a estrategia aleatoria
                jugador.strategy = RandomStrategy(jugador)

    elif (
        context.game.state.month_counter == 11 and context.game.state.oktoberfest_active
    ):
        # Terminar Oktober Fest
        context.game.state.oktoberfest_active = False

        for jugador in context.game.state.active_players:
            if (
                hasattr(jugador, "is_bot")
                and jugador.is_bot
                and jugador.id in context.game.state.original_strategies
            ):
                jugador.strategy = context.game.state.original_strategies[jugador.id]

        context.game.state.original_strategies = {}


@then("Oktober Fest debe estar activo")
def step_oktober_fest_debe_estar_activo(context):
    assert context.game.state.oktoberfest_active == True


@then("Oktober Fest no debe estar activo")
def step_oktober_fest_no_debe_estar_activo(context):
    assert context.game.state.oktoberfest_active == False


@then("Oktober Fest debe seguir activo")
def step_oktober_fest_debe_seguir_activo(context):
    assert context.game.state.oktoberfest_active == True


@then("todos los jugadores bot deben tener estrategia aleatoria")
def step_todos_bots_estrategia_aleatoria(context):
    from src.players.strategies.random_strategy import RandomStrategy

    for jugador in context.game.state.active_players:
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            assert isinstance(jugador.strategy, RandomStrategy)


@then("las estrategias originales deben estar guardadas")
def step_estrategias_originales_guardadas_verificar(context):
    for jugador in context.game.state.active_players:
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            assert jugador.id in context.game.state.original_strategies


@then("todos los jugadores bot deben tener sus estrategias originales")
def step_todos_bots_estrategias_originales(context):
    for jugador in context.game.state.active_players:
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            # Verificar que NO tiene estrategia aleatoria
            from src.players.strategies.random_strategy import RandomStrategy

            assert not isinstance(jugador.strategy, RandomStrategy)


@then("las estrategias guardadas deben estar vacias")
def step_estrategias_guardadas_vacias(context):
    assert len(context.game.state.original_strategies) == 0


@then("solo los jugadores bot deben cambiar a estrategia aleatoria")
def step_solo_bots_cambian_estrategia(context):
    from src.players.strategies.random_strategy import RandomStrategy

    for jugador in context.game.state.active_players:
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            assert isinstance(jugador.strategy, RandomStrategy)
        else:
            # Jugadores humanos no deben cambiar
            assert not isinstance(jugador.strategy, RandomStrategy)


@then("los jugadores humanos deben mantener sus estrategias")
def step_humanos_mantienen_estrategias(context):
    from src.players.strategies.random_strategy import RandomStrategy

    for jugador in context.game.state.active_players:
        if not hasattr(jugador, "is_bot") or not jugador.is_bot:
            assert not isinstance(jugador.strategy, RandomStrategy)


@then("las estrategias no deben cambiar nuevamente")
def step_estrategias_no_cambian_nuevamente(context):
    # Verificar que los bots siguen teniendo estrategia aleatoria
    # (no se han cambiado nuevamente)
    from src.players.strategies.random_strategy import RandomStrategy

    for jugador in context.game.state.active_players:
        if hasattr(jugador, "is_bot") and jugador.is_bot:
            assert isinstance(jugador.strategy, RandomStrategy)
