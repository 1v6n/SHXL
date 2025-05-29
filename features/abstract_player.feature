Feature: Funcionalidad del jugador abstracto

  Como sistema de juego,
  quiero que la clase Player abstracta proporcione la base para todos los tipos de jugadores,
  para asegurar que tengan las propiedades y métodos necesarios para el juego.

  Scenario: Inicialización básica de jugador
    Given un jugador abstracto con ID 1, nombre "Test Player", role "liberal", y estado de juego
    Then el jugador debe tener ID 1
    And el jugador debe tener nombre "Test Player"
    And el jugador debe tener role "liberal"
    And el jugador no debe estar muerto
    And el contador de jugadores conocidos debe estar inicializado

  Scenario: Propiedades de jugador liberal
    Given un jugador con party membership "liberal"
    Then el jugador debe ser liberal
    And el jugador no debe ser fascista
    And el jugador no debe ser comunista
    And el jugador no debe ser hitler

  Scenario: Propiedades de jugador fascista
    Given un jugador con party membership "fascist"
    Then el jugador debe ser fascista
    And el jugador no debe ser liberal
    And el jugador no debe ser comunista
    And el jugador no debe ser hitler

  Scenario: Propiedades de jugador comunista
    Given un jugador con party membership "communist"
    Then el jugador debe ser comunista
    And el jugador no debe ser liberal
    And el jugador no debe ser fascista
    And el jugador no debe ser hitler

  Scenario: Propiedades de Hitler
    Given un jugador con role "hitler" y party membership "fascist"
    Then el jugador debe ser hitler
    And el jugador debe ser fascista
    And el jugador no debe ser liberal
    And el jugador no debe ser comunista

  Scenario: Inicialización de atributos de fascista normal
    Given un estado de juego con 6 jugadores
    And un jugador fascista que no es hitler
    When se inicializan los atributos del role
    Then el jugador debe tener lista de fascistas inicializada
    And el jugador debe tener referencia a hitler inicializada

  Scenario: Inicialización de atributos de Hitler en juego pequeño
    Given un estado de juego con 5 jugadores
    And un jugador hitler
    When se inicializan los atributos del role
    Then el jugador debe tener lista de fascistas inicializada

  Scenario: Inicialización de atributos de Hitler en juego grande
    Given un estado de juego con 9 jugadores
    And un jugador hitler
    When se inicializan los atributos del role
    Then el jugador no debe conocer a otros fascistas

  Scenario: Inicialización de atributos de comunista en juego pequeño
    Given un estado de juego con 7 jugadores
    And un jugador comunista
    When se inicializan los atributos del role
    Then el jugador debe tener lista de comunistas conocidos inicializada

  Scenario: Inicialización de atributos de comunista en juego grande
    Given un estado de juego con 11 jugadores
    And un jugador comunista
    When se inicializan los atributos del role
    Then el jugador no debe conocer a otros comunistas

  Scenario: Gestión de conocimiento de jugadores inspeccionados
    Given un jugador abstracto inicializado
    When el jugador inspecciona al jugador 2 como "fascist"
    Then el jugador debe conocer que el jugador 2 es "fascist"
    And el diccionario de jugadores inspeccionados debe contener al jugador 2

  Scenario: Gestión de afiliaciones conocidas
    Given un jugador abstracto inicializado
    When se registra que el jugador 3 tiene afiliación "liberal"
    Then el jugador debe conocer que el jugador 3 es "liberal"
    And el diccionario de afiliaciones conocidas debe contener al jugador 3

  Scenario: Verificación de conocimiento de Hitler
    Given un jugador fascista inicializado
    When se asigna hitler como el jugador 4
    Then el jugador debe conocer a hitler
    And knows_hitler debe retornar True

  Scenario: Verificación de conocimiento de Hitler sin asignar
    Given un jugador fascista inicializado
    When hitler no está asignado
    Then el jugador no debe conocer a hitler
    And knows_hitler debe retornar False

  Scenario: Representación en string del jugador
    Given un jugador abstracto con ID 1, nombre "Test Player", role "liberal", y estado de juego
    Then la representación string debe contener el ID, nombre y role

  Scenario: Métodos abstractos deben estar definidos
    Given un jugador abstracto inicializado
    Then debe tener método abstracto nominate_chancellor
    And debe tener método abstracto filter_policies
    And debe tener método abstracto choose_policy
    And debe tener método abstracto vote
    And debe tener método abstracto veto
    And debe tener método abstracto accept_veto
    And debe tener método abstracto view_policies
    And debe tener método abstracto kill
    And debe tener método abstracto choose_player_to_mark
    And debe tener método abstracto inspect_player
    And debe tener método abstracto choose_next
    And debe tener método abstracto choose_player_to_radicalize
    And debe tener método abstracto propaganda_decision
    And debe tener método abstracto choose_revealer
    And debe tener método abstracto social_democratic_removal_choice
