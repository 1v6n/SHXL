Feature: Gestión de salas de juego
  Como jugador
  Quiero crear y unirme a salas de juego
  Para poder participar en partidas

  Background:
    Given el servidor de juego está en funcionamiento

  # Scenarios de creación de juego
  Scenario: Crear una nueva sala desde el endpoint /newgame
    When el cliente envía una petición POST a /newgame con 8 jugadores y estrategia "smart"
    Then el sistema responde con estado 201
    And el cuerpo contiene un gameID
    And el estado inicial es "waiting_for_players"
    And la cantidad máxima de jugadores es 8

  # Scenarios de unirse a juego
  Scenario: Unirse exitosamente a una sala con lugar disponible
    Given existe una sala de juego con 4 lugares máximos
    When el cliente envía una petición POST para unirse con nombre "Alice"
    Then el sistema responde con estado 200
    And el cuerpo contiene un playerId
    And el cuerpo contiene currentPlayers mayor a 0
    And el cuerpo contiene maxPlayers igual a 4

  Scenario: Rechazar unión por nombre faltante
    Given existe una sala de juego con 4 lugares máximos
    When el cliente envía una petición POST para unirse sin nombre
    Then el sistema responde con estado 400
    And el cuerpo contiene error "Missing playerName"

  Scenario: Rechazar unión por sala inexistente
    When el cliente envía una petición POST a /games/invalid123/join con nombre "Bob"
    Then el sistema responde con estado 404
    And el cuerpo contiene error "Game not found"

  Scenario: Crear sala y llenarla completamente
    When el cliente envía una petición POST a /newgame con 2 jugadores y estrategia "smart"
    Then el sistema responde con estado 201
    And el cuerpo contiene un gameID
    When el cliente llena la sala hasta su capacidad máxima
    And el cliente envía una petición POST para unirse con nombre "Overflow"
    Then el sistema responde con estado 403
    And el cuerpo contiene error "Game is full"

  # Scenario combinado: crear y unirse en flujo completo
  Scenario: Flujo completo - crear sala y que se una un jugador
    When el cliente envía una petición POST a /newgame con 6 jugadores y estrategia "smart"
    Then el sistema responde con estado 201
    And el cuerpo contiene un gameID
    When el cliente envía una petición POST para unirse con nombre "Alice"
    Then el sistema responde con estado 200
    And el cuerpo contiene un playerId
    And el cuerpo contiene maxPlayers igual a 6
