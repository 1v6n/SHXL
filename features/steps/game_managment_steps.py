"""
Game Management Steps for BDD Testing

Este módulo contiene los steps de Behave para probar la funcionalidad de gestión
de salas de juego, incluyendo creación de salas y unión de jugadores.

Complementa create_game_steps.py proporcionando steps más genéricos y funcionalidad
adicional para testing de joins y manejo de errores.

Example:
    Para usar estos steps en un feature:

        Given existe una sala de juego con 8 lugares máximos
        When el cliente envía una petición POST para unirse con nombre "Alice"
        Then el sistema responde con estado 200
        And el cuerpo contiene un playerId
"""

import requests
from behave import given, then, when

# ============================================================================
# STEPS PARA GESTIÓN DE JUEGOS (complementan create_game_steps.py)
# ============================================================================

@when('el cliente envía una petición POST a /newgame con {player_count:d} jugadores y estrategia "{strategy}"')
def step_impl_post_newgame_generic(context, player_count, strategy):
    """Crear juego con cualquier número de jugadores.

    Step genérico para crear salas de juego con configuración personalizada.
    Guarda el gameID en el contexto para uso posterior en otros steps.

    Args:
        context: Contexto de Behave con información compartida entre steps
        player_count (int): Número máximo de jugadores para la sala
        strategy (str): Estrategia de IA a usar ("smart", "random", etc.)

    Side Effects:
        - Establece context.current_game_id con el ID del juego creado
        - Establece context.current_max_players con el límite de jugadores
        - context.response contiene la respuesta HTTP del servidor

    Example:
        When el cliente envía una petición POST a /newgame con 8 jugadores y estrategia "smart"
    """
    payload = {
        "playerCount": player_count,
        "strategy": strategy
    }
    context.response = requests.post(
        f"{context.base_url}/newgame",
        json=payload,
        timeout=15
    )

    if context.response.status_code == 201:
        game_data = context.response.json()
        context.current_game_id = game_data["gameID"]
        context.current_max_players = player_count


@given('existe una sala de juego con {max_players:d} lugares máximos')
def step_impl_create_test_game(context, max_players):
    """Crear una sala de juego para testing de funcionalidad join.

    Crea una nueva sala de juego usando el endpoint /newgame y guarda
    el ID para uso posterior en steps de join. Úsala cuando necesites
    una sala existente para probar la funcionalidad de unirse.

    Args:
        context: Contexto de Behave con información compartida
        max_players (int): Número máximo de jugadores para la sala de prueba

    Raises:
        AssertionError: Si la creación de la sala falla (status != 201)

    Side Effects:
        - Establece context.current_game_id con el ID del juego creado
        - Establece context.current_max_players con el límite configurado

    Example:
        Given existe una sala de juego con 8 lugares máximos
    """
    payload = {
        "playerCount": max_players,
        "strategy": "smart"
    }
    response = requests.post(
        f"{context.base_url}/newgame",
        json=payload,
        timeout=10
    )

    assert response.status_code == 201, f"Failed to create game: {response.text}"

    game_data = response.json()
    context.current_game_id = game_data["gameID"]
    context.current_max_players = max_players


@when('el cliente envía una petición POST para unirse con nombre "{player_name}"')
def step_impl_post_join_current_game(context, player_name):
    """Unirse al juego actual usando el gameID guardado en contexto.

    Envía una petición para unirse a la sala de juego que fue creada
    previamente y cuyo ID está guardado en context.current_game_id.

    Args:
        context: Contexto de Behave que debe contener current_game_id
        player_name (str): Nombre del jugador que se quiere unir

    Requires:
        context.current_game_id: ID de la sala de juego existente
        context.base_url: URL base del servidor de juego

    Side Effects:
        - context.response contiene la respuesta HTTP del servidor

    Example:
        When el cliente envía una petición POST para unirse con nombre "Alice"
    """
    payload = {"playerName": player_name}
    context.response = requests.post(
        f"{context.base_url}/games/{context.current_game_id}/join",
        json=payload,
        timeout=10
    )


@when('el cliente envía una petición POST para unirse sin nombre')
def step_impl_post_join_no_name_current_game(context):
    """Unirse sin nombre al juego actual para probar validación.

    Envía una petición de join sin proporcionar playerName para probar
    que el servidor rechaza correctamente requests inválidos.

    Args:
        context: Contexto de Behave que debe contener current_game_id

    Requires:
        context.current_game_id: ID de la sala de juego existente

    Side Effects:
        - context.response contiene la respuesta HTTP (esperada: 400)

    Example:
        When el cliente envía una petición POST para unirse sin nombre
    """
    payload = {}
    context.response = requests.post(
        f"{context.base_url}/games/{context.current_game_id}/join",
        json=payload,
        timeout=10
    )


@when('el cliente envía una petición POST a /games/{game_id}/join con nombre "{player_name}"')
def step_impl_post_join_specific_game(context, game_id, player_name):
    """Unirse a un juego específico por ID.

    Usado principalmente para probar scenarios donde se intenta unirse
    a salas inexistentes o con IDs inválidos.

    Args:
        context: Contexto de Behave con información compartida
        game_id (str): ID específico de la sala (puede ser inválido)
        player_name (str): Nombre del jugador que intenta unirse

    Side Effects:
        - context.response contiene la respuesta HTTP del servidor

    Example:
        When el cliente envía una petición POST a /games/invalid123/join con nombre "Bob"
    """
    payload = {"playerName": player_name}
    context.response = requests.post(
        f"{context.base_url}/games/{game_id}/join",
        json=payload,
        timeout=10
    )


@when('el cliente llena la sala hasta su capacidad máxima')
def step_impl_fill_game_to_capacity(context):
    """Llenar la sala hasta el máximo de jugadores.

    Agrega jugadores automaticamente hasta que la sala esté llena,
    usado para probar el scenario de "sala llena" donde el siguiente
    jugador debería ser rechazado.

    Args:
        context: Contexto que debe contener current_game_id y current_max_players

    Requires:
        context.current_game_id: ID de la sala a llenar
        context.current_max_players: Límite máximo de jugadores

    Note:
        Itera hasta max_players + 5 para asegurar que la sala se llene
        completamente, sin importar cuántos jugadores AI existan.

    Example:
        When el cliente llena la sala hasta su capacidad máxima
    """
    max_players = context.current_max_players
    for i in range(max_players + 5):
        payload = {"playerName": f"Filler{i+1}"}
        response = requests.post(
            f"{context.base_url}/games/{context.current_game_id}/join",
            json=payload,
            timeout=10
        )
        if response.status_code == 403:  # Game is full
            break


# ============================================================================
# STEPS DE VERIFICACIÓN (complementan los de create_game_steps.py)
# ============================================================================

@then("el sistema responde con estado {status_code:d}")
def step_impl_status_code_generic(context, status_code):
    """Verificar cualquier código de estado HTTP.

    Step genérico para validar el código de respuesta HTTP del servidor.
    Proporciona mensaje de error detallado en caso de fallo.

    Args:
        context: Contexto que debe contener la respuesta HTTP
        status_code (int): Código de estado HTTP esperado

    Raises:
        AssertionError: Si el código de estado no coincide con el esperado

    Example:
        Then el sistema responde con estado 200
        Then el sistema responde con estado 404
    """
    assert context.response.status_code == status_code, \
        f"Expected {status_code}, got {context.response.status_code}. Response: {context.response.text}"


@then("la cantidad máxima de jugadores es {expected:d}")
def step_impl_max_players_generic(context, expected):
    """Verificar maxPlayers para cualquier número.

    Valida que la respuesta JSON contiene el campo maxPlayers con
    el valor esperado.

    Args:
        context: Contexto con la respuesta HTTP que contiene JSON
        expected (int): Número esperado de jugadores máximos

    Raises:
        AssertionError: Si maxPlayers no existe o no coincide

    Example:
        Then la cantidad máxima de jugadores es 8
    """
    body = context.response.json()
    assert "maxPlayers" in body, f"No maxPlayers in response: {body}"
    assert body["maxPlayers"] == expected, \
        f"Expected maxPlayers {expected}, got {body['maxPlayers']}"


@then("el cuerpo contiene un playerId")
def step_impl_body_contains_player_id(context):
    """Verificar que la respuesta contiene un playerId válido.

    Valida que la respuesta JSON incluye el campo playerId y que
    es un entero válido, indicando que el jugador fue creado exitosamente.

    Args:
        context: Contexto con la respuesta HTTP JSON

    Raises:
        AssertionError: Si playerId no existe o no es un entero

    Example:
        Then el cuerpo contiene un playerId
    """
    body = context.response.json()
    assert "playerId" in body, f"No playerId in response: {body}"
    assert isinstance(body["playerId"], int), \
        f"playerId should be int, got {type(body['playerId'])}: {body['playerId']}"


@then("el cuerpo contiene currentPlayers mayor a {expected:d}")
def step_impl_current_players_greater(context, expected):
    """Verificar que hay más jugadores que el mínimo esperado.

    Útil para validar que al menos hay cierto número de jugadores
    en la sala sin necesidad de especificar el número exacto.

    Args:
        context: Contexto con la respuesta HTTP JSON
        expected (int): Número mínimo de jugadores esperados

    Raises:
        AssertionError: Si currentPlayers no existe o es menor/igual al mínimo

    Example:
        Then el cuerpo contiene currentPlayers mayor a 0
    """
    body = context.response.json()
    assert "currentPlayers" in body, f"No currentPlayers in response: {body}"
    assert body["currentPlayers"] > expected, \
        f"Expected currentPlayers > {expected}, got {body['currentPlayers']}"


@then("el cuerpo contiene currentPlayers igual a {expected:d}")
def step_impl_current_players_equal(context, expected):
    """Verificar el número exacto de jugadores.

    Valida que el número actual de jugadores en la sala coincide
    exactamente con el valor esperado.

    Args:
        context: Contexto con la respuesta HTTP JSON
        expected (int): Número exacto de jugadores esperados

    Raises:
        AssertionError: Si currentPlayers no coincide exactamente

    Example:
        Then el cuerpo contiene currentPlayers igual a 3
    """
    body = context.response.json()
    assert "currentPlayers" in body, f"No currentPlayers in response: {body}"
    assert body["currentPlayers"] == expected, \
        f"Expected currentPlayers {expected}, got {body['currentPlayers']}"


@then("el cuerpo contiene maxPlayers igual a {expected:d}")
def step_impl_max_players_equal(context, expected):
    """Verificar maxPlayers exacto.

    Alternativa al step genérico para validar el número máximo
    de jugadores permitidos en la sala.

    Args:
        context: Contexto con la respuesta HTTP JSON
        expected (int): Número máximo de jugadores esperado

    Raises:
        AssertionError: Si maxPlayers no coincide exactamente

    Example:
        Then el cuerpo contiene maxPlayers igual a 8
    """
    body = context.response.json()
    assert "maxPlayers" in body, f"No maxPlayers in response: {body}"
    assert body["maxPlayers"] == expected, \
        f"Expected maxPlayers {expected}, got {body['maxPlayers']}"


@then('el cuerpo contiene error "{error_message}"')
def step_impl_error_message(context, error_message):
    """Verificar mensaje de error específico.

    Valida que la respuesta contiene un mensaje de error específico,
    útil para probar validaciones y casos de error controlados.

    Args:
        context: Contexto con la respuesta HTTP JSON
        error_message (str): Mensaje de error esperado

    Raises:
        AssertionError: Si el error no existe o no coincide

    Example:
        Then el cuerpo contiene error "Missing playerName"
        Then el cuerpo contiene error "Game not found"
    """
    body = context.response.json()
    assert "error" in body, f"No error field in response: {body}"
    assert body["error"] == error_message, \
        f"Expected error '{error_message}', got '{body['error']}'"

# Agregar estos steps al final del archivo

# ============================================================================
# STEPS PARA INICIAR PARTIDA
# ============================================================================

@given('se han unido {player_count:d} jugadores a la sala')
def step_impl_add_players_to_room(context, player_count):
    """Agregar jugadores humanos a la sala actual.

    Agrega el número especificado de jugadores humanos a la sala
    guardada en context.current_game_id.

    Args:
        context: Contexto que debe contener current_game_id
        player_count (int): Número de jugadores a agregar

    Requires:
        context.current_game_id: ID de la sala existente

    Side Effects:
        - Agrega jugadores con nombres Player1, Player2, etc.
        - context.current_players_added guarda el número agregado

    Example:
        Given se han unido 5 jugadores a la sala
    """
    for i in range(player_count):
        payload = {"playerName": f"Player{i+1}"}
        response = requests.post(
            f"{context.base_url}/games/{context.current_game_id}/join",
            json=payload,
            timeout=10
        )
        assert response.status_code == 200, f"Failed to add player {i+1}: {response.text}"

    context.current_players_added = player_count


@given('la partida ya ha sido iniciada')
def step_impl_game_already_started(context):
    """Marcar la partida como ya iniciada.

    Inicia la partida actual para poder probar scenarios donde se
    intenta iniciar una partida que ya está en progreso.

    Args:
        context: Contexto que debe contener current_game_id

    Requires:
        context.current_game_id: ID de la sala con jugadores suficientes

    Side Effects:
        - La partida cambia a estado "in_progress"

    Example:
        Given la partida ya ha sido iniciada
    """
    payload = {"hostPlayerID": 0}
    response = requests.post(
        f"{context.base_url}/games/{context.current_game_id}/start",
        json=payload,
        timeout=10
    )
    assert response.status_code == 200, f"Failed to start game: {response.text}"


@when('el anfitrión envía una petición POST para iniciar la partida')
def step_impl_host_starts_game(context):
    """El anfitrión inicia la partida.

    Envía una petición para iniciar la partida usando hostPlayerID = 0
    (el anfitrión siempre es el primer jugador).

    Args:
        context: Contexto que debe contener current_game_id

    Requires:
        context.current_game_id: ID de la sala existente

    Side Effects:
        - context.response contiene la respuesta HTTP del servidor

    Example:
        When el anfitrión envía una petición POST para iniciar la partida
    """
    payload = {"hostPlayerID": 0}
    context.response = requests.post(
        f"{context.base_url}/games/{context.current_game_id}/start",
        json=payload,
        timeout=10
    )


@when('un jugador no-anfitrión envía una petición POST para iniciar la partida')
def step_impl_non_host_starts_game(context):
    """Un jugador que no es anfitrión intenta iniciar la partida.

    Envía una petición para iniciar usando un hostPlayerID != 0 para
    probar que solo el anfitrión puede iniciar la partida.

    Args:
        context: Contexto que debe contener current_game_id

    Side Effects:
        - context.response contiene la respuesta HTTP (esperada: 403)

    Example:
        When un jugador no-anfitrión envía una petición POST para iniciar la partida
    """
    payload = {"hostPlayerID": 1}  # No es el anfitrión
    context.response = requests.post(
        f"{context.base_url}/games/{context.current_game_id}/start",
        json=payload,
        timeout=10
    )


@when('se envía una petición POST sin hostPlayerID para iniciar la partida')
def step_impl_start_game_no_host_id(context):
    """Iniciar partida sin proporcionar hostPlayerID.

    Envía una petición sin el campo requerido hostPlayerID para probar
    la validación de parámetros.

    Args:
        context: Contexto que debe contener current_game_id

    Side Effects:
        - context.response contiene la respuesta HTTP (esperada: 400)

    Example:
        When se envía una petición POST sin hostPlayerID para iniciar la partida
    """
    payload = {}  # Sin hostPlayerID
    context.response = requests.post(
        f"{context.base_url}/games/{context.current_game_id}/start",
        json=payload,
        timeout=10
    )


@then('el cuerpo contiene state "{expected_state}"')
def step_impl_body_contains_state(context, expected_state):
    """Verificar el estado del juego en la respuesta.

    Valida que la respuesta JSON contiene el campo state con
    el valor esperado.

    Args:
        context: Contexto con la respuesta HTTP JSON
        expected_state (str): Estado esperado del juego

    Raises:
        AssertionError: Si state no existe o no coincide

    Example:
        Then el cuerpo contiene state "in_progress"
    """
    body = context.response.json()
    assert "state" in body, f"No state field in response: {body}"
    assert body["state"] == expected_state, \
        f"Expected state '{expected_state}', got '{body['state']}'"


@then('el cuerpo contiene roles_assigned {expected_value}')
def step_impl_body_contains_roles_assigned(context, expected_value):
    """Verificar que los roles han sido asignados.

    Valida que la respuesta contiene roles_assigned con el valor
    booleano esperado.

    Args:
        context: Contexto con la respuesta HTTP JSON
        expected_value (str): "true" o "false"

    Raises:
        AssertionError: Si roles_assigned no existe o no coincide

    Example:
        Then el cuerpo contiene roles_assigned true
    """
    body = context.response.json()
    expected_bool = expected_value.lower() == "true"
    assert "roles_assigned" in body, f"No roles_assigned field in response: {body}"
    assert body["roles_assigned"] == expected_bool, \
        f"Expected roles_assigned {expected_bool}, got {body['roles_assigned']}"


@then('el cuerpo contiene deck_ready {expected_value}')
def step_impl_body_contains_deck_ready(context, expected_value):
    """Verificar que el mazo está listo.

    Valida que la respuesta contiene deck_ready con el valor
    booleano esperado.

    Args:
        context: Contexto con la respuesta HTTP JSON
        expected_value (str): "true" o "false"

    Raises:
        AssertionError: Si deck_ready no existe o no coincide

    Example:
        Then el cuerpo contiene deck_ready true
    """
    body = context.response.json()
    expected_bool = expected_value.lower() == "true"
    assert "deck_ready" in body, f"No deck_ready field in response: {body}"
    assert body["deck_ready"] == expected_bool, \
        f"Expected deck_ready {expected_bool}, got {body['deck_ready']}"

@when('el anfitrión envía una petición POST a /games/invalid123/start')
def step_impl_start_invalid_game(context):
    """Intentar iniciar un juego con ID inválido.

    Envía una petición para iniciar una partida usando un gameID que
    no existe, para probar el manejo de errores 404.

    Args:
        context: Contexto de Behave con información compartida

    Side Effects:
        - context.response contiene la respuesta HTTP (esperada: 404)

    Example:
        When el anfitrión envía una petición POST a /games/invalid123/start
    """
    payload = {"hostPlayerID": 0}
    context.response = requests.post(
        f"{context.base_url}/games/invalid123/start",
        json=payload,
        timeout=10
    )


@when('se unen {player_count:d} jugadores adicionales a la sala')
def step_impl_add_additional_players(context, player_count):
    """Agregar jugadores adicionales a la sala.

    Agrega el número especificado de jugadores adicionales a la sala
    actual. Útil para scenarios de flujo completo donde ya hay algunos
    jugadores y se necesitan más.

    Args:
        context: Contexto que debe contener current_game_id
        player_count (int): Número de jugadores adicionales a agregar

    Requires:
        context.current_game_id: ID de la sala existente

    Side Effects:
        - Agrega jugadores con nombres ExtraPlayer1, ExtraPlayer2, etc.
        - Actualiza context.current_players_added con el total

    Example:
        When se unen 5 jugadores adicionales a la sala
    """
    # Obtener el número base de jugadores ya agregados
    base_number = getattr(context, 'current_players_added', 0)

    for i in range(player_count):
        payload = {"playerName": f"ExtraPlayer{base_number + i + 1}"}
        response = requests.post(
            f"{context.base_url}/games/{context.current_game_id}/join",
            json=payload,
            timeout=10
        )
        assert response.status_code == 200, f"Failed to add extra player {i+1}: {response.text}"

    # Actualizar contador total de jugadores agregados
    context.current_players_added = base_number + player_count
