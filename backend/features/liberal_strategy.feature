Feature: Funcionalidad de la estrategia liberal

  Como implementación de estrategia de jugador liberal,
  quiero tomar decisiones estratégicas basadas en información conocida y confianza,
  para ayudar al equipo liberal a ganar el juego mediante políticas liberales y eliminar fascistas.

  Scenario: Inicialización de estrategia liberal
    Given un jugador liberal mock
    When creo una estrategia liberal con el jugador
    Then la estrategia liberal debe estar inicializada correctamente
    And la estrategia liberal debe heredar de PlayerStrategy

  Scenario: Nominación de canciller priorizando jugadores confiables
    Given una estrategia liberal
    And una lista de 4 jugadores elegibles para canciller
    And el jugador 2 es conocido como liberal
    And el jugador 3 es conocido como fascista
    When la estrategia liberal nomina un canciller
    Then debe retornar el jugador liberal conocido
    And no debe elegir el jugador fascista conocido

  Scenario: Nominación de canciller evitando fascistas conocidos
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para canciller
    And el jugador 1 es conocido como fascista
    And el jugador 2 es conocido como fascista
    When la estrategia liberal nomina un canciller
    Then debe retornar el jugador 3
    And no debe elegir jugadores fascistas conocidos

  Scenario: Nominación de canciller sin información
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para canciller sin información
    When la estrategia liberal nomina un canciller
    Then debe retornar uno de los jugadores elegibles liberal
    And el resultado debe ser aleatorio entre los elegibles

  Scenario: Filtrado de políticas priorizando liberales
    Given una estrategia liberal
    And una lista de 3 políticas: "liberal", "fascist", "communist"
    When la estrategia liberal filtra las políticas
    Then debe mantener la política liberal
    And debe descartar la política fascista
    And debe retornar 2 políticas para pasar

  Scenario: Filtrado de políticas sin liberales
    Given una estrategia liberal
    And una lista de 3 políticas: "fascist", "communist", "fascist"
    When la estrategia liberal filtra las políticas
    Then debe mantener la política comunista
    And debe descartar una política fascista
    And debe retornar 2 políticas para pasar

  Scenario: Selección de política priorizando liberal
    Given una estrategia liberal
    And una lista de 2 políticas: "liberal", "fascist"
    When la estrategia liberal elige una política
    Then debe promulgar la política liberal
    And debe descartar la política fascista

  Scenario: Selección de política entre comunista y fascista
    Given una estrategia liberal
    And una lista de 2 políticas: "communist", "fascist"
    When la estrategia liberal elige una política
    Then debe promulgar la política comunista
    And debe descartar la política fascista

  Scenario: Votación positiva con jugadores confiables
    Given una estrategia liberal
    And un presidente liberal conocido como liberal
    And un canciller liberal conocido como liberal
    When la estrategia liberal vota en el gobierno
    Then debe votar positivamente

  Scenario: Votación negativa con canciller fascista conocido
    Given una estrategia liberal
    And un presidente liberal conocido como liberal
    And un canciller liberal conocido como fascista
    When la estrategia liberal vota en el gobierno
    Then debe votar negativamente

  Scenario: Votación cautelosa en situación peligrosa
    Given una estrategia liberal
    And un presidente liberal sin información
    And un canciller liberal sin información
    And el estado del juego tiene 3 políticas fascistas
    When la estrategia liberal vota en el gobierno
    Then el voto debe ser cauteloso
    And la probabilidad de voto positivo debe ser baja

  Scenario: Votación optimista en juego temprano
    Given una estrategia liberal
    And un presidente liberal sin información
    And un canciller liberal sin información
    And el estado del juego tiene 0 políticas fascistas
    When la estrategia liberal vota en el gobierno
    Then el voto debe ser optimista
    And la probabilidad de voto positivo debe ser alta

  Scenario: Decisión de veto con todas las políticas fascistas
    Given una estrategia liberal
    And una lista de políticas para veto: "fascist", "fascist"
    When la estrategia liberal decide sobre veto
    Then debe proponer veto

  Scenario: Decisión de veto con políticas mixtas
    Given una estrategia liberal
    And una lista de políticas para veto: "liberal", "fascist"
    When la estrategia liberal decide sobre veto
    Then no debe proponer veto

  Scenario: Aceptación de veto con todas las políticas fascistas
    Given una estrategia liberal
    And una lista de políticas para veto: "fascist", "fascist"
    When la estrategia liberal decide aceptar veto
    Then debe aceptar el veto

  Scenario: Rechazo de veto con políticas no fascistas
    Given una estrategia liberal
    And una lista de políticas para veto: "liberal", "fascist"
    When la estrategia liberal decide aceptar veto
    Then no debe aceptar el veto

  Scenario: Ejecución de fascista conocido
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para ejecución
    And el jugador 2 es conocido como fascista
    When la estrategia liberal elige un jugador para ejecutar
    Then debe elegir el jugador fascista conocido

  Scenario: Ejecución sin fascistas conocidos
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para ejecución sin información
    When la estrategia liberal elige un jugador para ejecutar
    Then debe elegir uno de los jugadores no inspeccionados
    And el resultado debe ser de jugadores sin información

  Scenario: Inspección de jugador no inspeccionado
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para inspección
    And el jugador 1 ya fue inspeccionado como liberal
    When la estrategia liberal elige un jugador para inspeccionar
    Then debe elegir un jugador no inspeccionado
    And no debe elegir el jugador ya inspeccionado

  Scenario: Selección de próximo presidente liberal conocido
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para presidencia
    And el jugador 2 es conocido como liberal
    When la estrategia liberal elige el siguiente presidente
    Then debe elegir el jugador liberal conocido

  Scenario: Radicalización de fascista conocido
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para radicalización
    And el jugador 2 es conocido como fascista
    When la estrategia liberal elige un jugador para radicalizar
    Then debe elegir el jugador fascista conocido

  Scenario: Marcado para ejecución de fascista
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para marcado
    And el jugador 2 es conocido como fascista
    When la estrategia liberal elige un jugador para marcar
    Then debe elegir el jugador fascista conocido

  Scenario: Espionaje de jugador no inspeccionado
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para espionaje
    And el jugador 1 ya fue inspeccionado
    When la estrategia liberal elige un jugador para espionar
    Then debe elegir un jugador no inspeccionado

  Scenario: Decisión de propaganda con política fascista
    Given una estrategia liberal
    And una política fascista para propaganda
    When la estrategia liberal decide sobre propaganda
    Then debe descartar la política fascista en propaganda

  Scenario: Decisión de propaganda con política liberal
    Given una estrategia liberal
    And una política liberal para propaganda
    When la estrategia liberal decide sobre propaganda
    Then no debe descartar la política liberal

  Scenario: Selección de revelador confiable
    Given una estrategia liberal
    And una lista de 3 jugadores elegibles para revelación
    And el jugador 2 es conocido como liberal
    When la estrategia liberal elige un revelador
    Then debe elegir el jugador liberal conocido

  Scenario: Perdón de liberal marcado
    Given una estrategia liberal
    And un jugador liberal conocido marcado para ejecución
    When la estrategia liberal decide sobre perdón
    Then debe perdonar al jugador liberal

  Scenario: No perdón de fascista marcado
    Given una estrategia liberal
    And un jugador fascista conocido marcado para ejecución
    When la estrategia liberal decide sobre perdón
    Then no debe perdonar al jugador fascista

  Scenario: Voto de no confianza con política liberal descartada
    Given una estrategia liberal
    And una política liberal como última descartada
    When la estrategia liberal decide sobre voto de no confianza
    Then debe votar para promulgar la política liberal

  Scenario: Voto de no confianza con política fascista descartada
    Given una estrategia liberal
    And una política fascista como última descartada
    When la estrategia liberal decide sobre voto de no confianza
    Then no debe votar para promulgar la política fascista

  Scenario: Remoción socialdemócrata priorizando fascistas
    Given una estrategia liberal
    And el estado tiene políticas fascistas y comunistas
    When la estrategia liberal elige qué remover en poder socialdemócrata
    Then debe elegir remover del track fascista
