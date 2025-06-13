Feature: Iniciar partida de juego SHXL
  Como anfitrión de una sala de juego
  Quiero poder iniciar la partida cuando estén todos listos
  Para que comience la fase de juego con roles asignados

  Background:
    Given el servidor de juego está en funcionamiento

  # Scenarios de inicio exitoso
  Scenario: Iniciar partida exitosamente con jugadores suficientes
    Given existe una sala de juego con 8 lugares máximos
    And se han unido 5 jugadores a la sala
    When el anfitrión envía una petición POST para iniciar la partida
    Then el sistema responde con estado 200
    And el cuerpo contiene state "in_progress"
    And el cuerpo contiene roles_assigned true
    And el cuerpo contiene deck_ready true
    And el cuerpo contiene currentPlayers mayor a 4

  Scenario: Iniciar partida llenando sala con jugadores AI
    Given existe una sala de juego con 6 lugares máximos
    And se han unido 5 jugadores a la sala
    When el anfitrión envía una petición POST para iniciar la partida
    Then el sistema responde con estado 200
    And el cuerpo contiene state "in_progress"
    And el cuerpo contiene currentPlayers igual a 6

  # Scenarios de validación de jugadores
  Scenario: Rechazar inicio con pocos jugadores
    Given existe una sala de juego con 8 lugares máximos
    And se han unido 2 jugadores a la sala
    When el anfitrión envía una petición POST para iniciar la partida
    Then el sistema responde con estado 403
    And el cuerpo contiene error "Need at least 5 players to start"

  Scenario: Rechazar inicio con sala vacía
    Given existe una sala de juego con 8 lugares máximos
    When el anfitrión envía una petición POST para iniciar la partida
    Then el sistema responde con estado 403
    And el cuerpo contiene error "No players in the game"

  # Scenarios de validación de permisos
  Scenario: Rechazar inicio si no eres el anfitrión
    Given existe una sala de juego con 8 lugares máximos
    And se han unido 6 jugadores a la sala
    When un jugador no-anfitrión envía una petición POST para iniciar la partida
    Then el sistema responde con estado 403
    And el cuerpo contiene error "Only the host can start the game"

  Scenario: Rechazar inicio con hostPlayerID faltante
    Given existe una sala de juego con 8 lugares máximos
    And se han unido 5 jugadores a la sala
    When se envía una petición POST sin hostPlayerID para iniciar la partida
    Then el sistema responde con estado 400
    And el cuerpo contiene error "Missing hostPlayerID"

  # Scenarios de estado del juego
  Scenario: Rechazar inicio de partida ya iniciada
    Given existe una sala de juego con 8 lugares máximos
    And se han unido 5 jugadores a la sala
    And la partida ya ha sido iniciada
    When el anfitrión envía una petición POST para iniciar la partida
    Then el sistema responde con estado 403
    And el cuerpo contiene error "Game already in progress"

  Scenario: Rechazar inicio en sala inexistente
    When el anfitrión envía una petición POST a /games/invalid123/start
    Then el sistema responde con estado 404
    And el cuerpo contiene error "Game not found"

  # Scenario de flujo completo
  Scenario: Flujo completo - crear sala, agregar jugadores e iniciar
    When el cliente envía una petición POST a /newgame con 7 jugadores y estrategia "smart"
    Then el sistema responde con estado 201
    And el cuerpo contiene un gameID
    When se unen 5 jugadores adicionales a la sala
    And el anfitrión envía una petición POST para iniciar la partida
    Then el sistema responde con estado 200
    And el cuerpo contiene state "in_progress"
    And el cuerpo contiene currentPlayers igual a 7
