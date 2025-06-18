Feature: Funcionalidad de la estrategia comunista

  Como implementación de estrategia de jugador comunista,
  quiero tomar decisiones estratégicas para promover políticas comunistas,
  para ayudar al equipo comunista a ganar el juego mediante políticas comunistas o radicalizando liberales.

  Scenario: Inicialización de estrategia comunista
    Given un jugador comunista mock
    When creo una estrategia comunista con el jugador
    Then la estrategia comunista debe estar inicializada correctamente
    And la estrategia comunista debe heredar de PlayerStrategy

  Scenario: Nominación de comunista si es posible
    Given una estrategia comunista
    And una lista de 3 jugadores elegibles para canciller (comunista)
    And el jugador 2 es comunista
    When la estrategia comunista nomina un canciller
    Then debe retornar un comunista como canciller
    And debe priorizar comunistas al nominar

  Scenario: Nominación de liberal si no hay comunistas elegibles
    Given una estrategia comunista
    And una lista de 3 jugadores elegibles para canciller (comunista)
    And ningún jugador es comunista
    And el jugador 1 es liberal
    When la estrategia comunista nomina un canciller
    Then debe retornar el jugador liberal
    And debe priorizar liberales antes que fascistas

  Scenario: Filtrado de políticas priorizando comunistas
    Given una estrategia comunista
    And una lista de 3 políticas: "communist", "liberal", "fascist"
    When la estrategia comunista filtra las políticas
    Then debe mantener la política comunista
    And debe descartar la política fascista

  Scenario: Filtrado de políticas sin comunistas
    Given una estrategia comunista
    And una lista de 3 políticas: "liberal", "fascist", "liberal"
    When la estrategia comunista filtra las políticas
    Then debe mantener una política liberal
    And debe descartar la política fascista

  Scenario: Selección de política priorizando comunista
    Given una estrategia comunista
    And una lista de 2 políticas: "communist", "liberal"
    When la estrategia comunista elige una política
    Then debe promulgar la política comunista
    And debe descartar la política liberal

  Scenario: Selección de política entre fascista y liberal
    Given una estrategia comunista
    And una lista de 2 políticas: "fascist", "liberal"
    When la estrategia comunista elige una política
    Then debe promulgar la política liberal
    And debe descartar la política fascista

  Scenario: Votación positiva con comunistas en el gobierno
    Given una estrategia comunista
    And un presidente comunista
    And un canciller comunista
    When la estrategia comunista vota en el gobierno
    Then debe votar positivamente para comunistas

  Scenario: Votación negativa con gobierno fascista conocido
    Given una estrategia comunista
    And un presidente fascista
    And un canciller fascista
    When la estrategia comunista vota en el gobierno
    Then debe votar negativamente contra fascistas

  Scenario: Decisión de veto sin políticas comunistas
    Given una estrategia comunista
    And una lista de políticas para veto comunista: "liberal", "fascist"
    When la estrategia comunista decide sobre veto
    Then debe proponer veto sin comunistas

  Scenario: Decisión de veto con políticas comunistas
    Given una estrategia comunista
    And una lista de políticas para veto: "communist", "liberal"
    When la estrategia comunista decide sobre veto
    Then no debe proponer veto con comunistas

  Scenario: Ejecución de fascista conocido
    Given una estrategia comunista
    And una lista de 3 jugadores elegibles para ejecución (comunista)
    And el jugador 2 es conocido como fascista
    When la estrategia comunista elige un jugador para ejecutar
    Then debe elegir el jugador fascista conocido (comunista)
    And debe priorizar fascistas para ejecución

  Scenario: Radicalización de liberal conocido
    Given una estrategia comunista
    And una lista de 3 jugadores elegibles para radicalización (comunista)
    And el jugador 2 es conocido como liberal
    When la estrategia comunista elige un jugador para radicalizar
    Then debe elegir el jugador liberal conocido (comunista)

  Scenario: Marcado de fascista para ejecución
    Given una estrategia comunista
    And una lista de 3 jugadores elegibles para marcado (comunista)
    And el jugador 2 es conocido como fascista
    When la estrategia comunista elige un jugador para marcar
    Then debe elegir el jugador fascista conocido (comunista)
    And debe usar mismo criterio que ejecución para comunistas

  Scenario: Espionaje de no comunistas no inspeccionados
    Given una estrategia comunista
    And una lista de 3 jugadores elegibles para espionaje (comunista)
    And el jugador 1 es comunista
    And el jugador 2 no fue inspeccionado
    When la estrategia comunista elige un jugador para espionar
    Then debe elegir un jugador no comunista no inspeccionado

  Scenario: Decisión de propaganda con política fascista
    Given una estrategia comunista
    And una política fascista para propaganda
    When la estrategia comunista decide sobre propaganda
    Then debe descartar la política fascista en propaganda

  Scenario: Decisión de propaganda con política comunista
    Given una estrategia comunista
    And una política comunista para propaganda
    When la estrategia comunista decide sobre propaganda
    Then no debe descartar la política comunista

  Scenario: Selección de comunista como revelador
    Given una estrategia comunista
    And una lista de 3 jugadores elegibles para revelación (comunista)
    And el jugador 2 es comunista
    When la estrategia comunista elige un revelador
    Then debe elegir el jugador comunista

  Scenario: Perdón de comunista marcado
    Given una estrategia comunista
    And un comunista está marcado para ejecución
    When la estrategia comunista decide sobre perdón
    Then debe perdonar al comunista

  Scenario: No perdón de fascista marcado
    Given una estrategia comunista
    And un fascista está marcado para ejecución
    When la estrategia comunista decide sobre perdón
    Then no debe perdonar al fascista

  Scenario: Propuesta de veto sin comunistas como canciller
    Given una estrategia comunista
    And políticas sin comunistas para propuesta de veto
    When la estrategia comunista propone veto como canciller
    Then debe proponer veto sin opciones comunistas

  Scenario: Remoción socialdemócrata priorizando fascistas
    Given una estrategia comunista
    And el estado tiene políticas fascistas y liberales
    When la estrategia comunista elige qué remover en poder socialdemócrata
    Then debe elegir remover del track fascista
    And debe debilitar a los fascistas primero
