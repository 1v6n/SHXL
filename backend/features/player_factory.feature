Feature: Creación y gestión de jugadores mediante PlayerFactory

  Como sistema de juego,
  quiero crear automáticamente jugadores con las estrategias apropiadas,
  para asegurar que cada jugador tenga el comportamiento correcto según su tipo y rol.

  Background:
    Given un estado de juego mock para factory

  Scenario: Crear jugador AI con estrategia por defecto
    When creo un jugador AI con ID 1, nombre "TestBot", sin rol, y estrategia "smart"
    Then el jugador debe ser una instancia de AIPlayer
    And el jugador debe tener ID 1
    And el jugador debe tener nombre "TestBot"
    And el jugador debe tener rol None

  Scenario: Crear jugador humano
    When creo un jugador humano con ID 2, nombre "TestPlayer", sin rol
    Then el jugador debe ser una instancia de HumanPlayer
    And el jugador debe tener ID 2
    And el jugador debe tener nombre "TestPlayer"
    And el jugador no debe tener atributo strategy

  Scenario: Aplicar estrategia random a jugador AI
    Given un jugador AI liberal sin estrategia asignada
    When aplico estrategia "random" al jugador
    Then el jugador debe usar estrategia RandomStrategy

  Scenario: Aplicar estrategia basada en rol - jugador liberal
    Given un jugador AI liberal sin estrategia asignada
    When aplico estrategia "role" al jugador
    Then el jugador debe usar estrategia LiberalStrategy

  Scenario: Aplicar estrategia basada en rol - jugador fascista
    Given un jugador AI fascista sin estrategia asignada
    When aplico estrategia "role" al jugador
    Then el jugador debe usar estrategia FascistStrategy

  Scenario: Aplicar estrategia basada en rol - jugador comunista
    Given un jugador AI comunista sin estrategia asignada
    When aplico estrategia "role" al jugador
    Then el jugador debe usar estrategia CommunistStrategy

  Scenario: Aplicar estrategia basada en rol - jugador Hitler
    Given un jugador AI hitler sin estrategia asignada
    When aplico estrategia "role" al jugador
    Then el jugador debe usar estrategia FascistStrategy

  Scenario: Aplicar estrategia smart por defecto
    Given un jugador AI liberal sin estrategia asignada
    When aplico estrategia "smart" al jugador
    Then el jugador debe usar estrategia SmartStrategy

  Scenario: No aplicar estrategia a jugador humano
    Given un jugador humano sin atributo strategy
    When aplico estrategia "smart" al jugador
    Then el jugador no debe tener atributo strategy

  Scenario: Crear múltiples jugadores AI
    When creo 4 jugadores con estrategia "smart" y sin jugadores humanos
    Then debo tener 4 jugadores en total
    And todos los jugadores deben ser instancias de AIPlayer
    And los nombres deben seguir el patrón "Bot {index}"
    And el estado debe almacenar la estrategia "smart"

  Scenario: Crear múltiples jugadores mixtos
    When creo 5 jugadores con estrategia "role" y jugadores humanos en posiciones [1, 3]
    Then debo tener 5 jugadores en total
    And el jugador en posición 0 debe ser AIPlayer con nombre "Bot 0"
    And el jugador en posición 1 debe ser HumanPlayer con nombre "Player 1"
    And el jugador en posición 2 debe ser AIPlayer con nombre "Bot 2"
    And el jugador en posición 3 debe ser HumanPlayer con nombre "Player 3"
    And el jugador en posición 4 debe ser AIPlayer con nombre "Bot 4"

  Scenario: Actualizar estrategias de múltiples jugadores
    Given una lista de 3 jugadores AI con roles [liberal, fascist, communist]
    When actualizo las estrategias de todos los jugadores con tipo "role"
    Then el jugador liberal debe usar estrategia LiberalStrategy
    And el jugador fascista debe usar estrategia FascistStrategy
    And el jugador comunista debe usar estrategia CommunistStrategy

  Scenario: Actualizar estrategias mixtas de jugadores AI y humanos
    Given una lista mixta de 4 jugadores [AI liberal, humano, AI fascista, AI comunista]
    When actualizo las estrategias de todos los jugadores con tipo "smart"
    Then el jugador AI liberal debe usar estrategia SmartStrategy
    And el jugador humano no debe tener cambios en strategy
    And el jugador AI fascista debe usar estrategia SmartStrategy
    And el jugador AI comunista debe usar estrategia SmartStrategy

  Scenario: Crear jugadores sin índices humanos especificados
    When creo 3 jugadores con estrategia "random" y jugadores humanos None
    Then debo tener 3 jugadores en total
    And todos los jugadores deben ser instancias de AIPlayer
    And todos los nombres deben seguir el patrón "Bot {index}"
