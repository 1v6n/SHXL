Feature: Funcionalidad de la estrategia fascista

  Como implementación de estrategia de jugador fascista,
  quiero tomar decisiones estratégicas para promover políticas fascistas y proteger a Hitler,
  para ayudar al equipo fascista a ganar el juego mediante políticas fascistas o colocando a Hitler como canciller.

  Scenario: Inicialización de estrategia fascista
    Given un jugador fascista mock
    When creo una estrategia fascista con el jugador
    Then la estrategia fascista debe estar inicializada correctamente
    And la estrategia fascista debe heredar de PlayerStrategy

  Scenario: Nominación de Hitler cuando es seguro
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para canciller
    And el jugador 2 es Hitler
    And el track fascista tiene 3 políticas
    When la estrategia fascista nomina un canciller
    Then debe retornar Hitler como canciller
    And debe priorizar a Hitler cuando es seguro

  Scenario: Nominación de fascista cuando Hitler no es seguro
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para canciller
    And el jugador 1 es fascista no Hitler
    And el jugador 2 es Hitler
    And el track fascista tiene 2 políticas
    When la estrategia fascista nomina un canciller
    Then debe retornar el fascista no Hitler
    And no debe elegir Hitler cuando no es seguro

  Scenario: Nominación cuando no hay fascistas elegibles
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles sin fascistas
    When la estrategia fascista nomina un canciller
    Then debe retornar uno de los jugadores elegibles fascista
    And debe elegir aleatoriamente entre no fascistas

  Scenario: Filtrado de políticas priorizando fascistas
    Given una estrategia fascista
    And una lista de 3 políticas: "fascist", "liberal", "communist"
    When la estrategia fascista filtra las políticas
    Then debe mantener la política fascista
    And debe descartar la política liberal
    And debe retornar 2 políticas para pasar

  Scenario: Filtrado de políticas sin fascistas
    Given una estrategia fascista
    And una lista de 3 políticas: "liberal", "communist", "liberal"
    When la estrategia fascista filtra las políticas
    Then debe mantener la política comunista
    And debe descartar una política liberal
    And debe priorizar comunista sobre liberal

  Scenario: Selección de política priorizando fascista
    Given una estrategia fascista
    And una lista de 2 políticas: "fascist", "liberal"
    When la estrategia fascista elige una política
    Then debe promulgar la política fascista
    And debe descartar la política liberal

  Scenario: Selección de política entre comunista y liberal
    Given una estrategia fascista
    And una lista de 2 políticas: "communist", "liberal"
    When la estrategia fascista elige una política
    Then debe promulgar la política comunista
    And debe descartar la política liberal

  Scenario: Votación positiva con canciller fascista
    Given una estrategia fascista
    And un presidente mock
    And un canciller fascista
    When la estrategia fascista vota en el gobierno
    Then debe votar positivamente para fascistas

  Scenario: Votación cautelosa con gobierno liberal conocido
    Given una estrategia fascista
    And un presidente conocido como liberal
    And un canciller conocido como liberal
    When la estrategia fascista vota en el gobierno
    Then debe votar cautelosamente contra liberales
    And la probabilidad de voto positivo debe ser muy baja

  Scenario: Votación estratégica cerca de poder fascista
    Given una estrategia fascista
    And un presidente mock
    And un canciller mock
    And el track fascista tiene 2 políticas
    When la estrategia fascista vota en el gobierno
    Then debe votar estratégicamente para obtener poder
    And la probabilidad de voto positivo debe ser alta

  Scenario: Decisión de veto sin políticas fascistas
    Given una estrategia fascista
    And una lista de políticas para veto: "liberal", "communist"
    When la estrategia fascista decide sobre veto
    Then debe proponer veto sin fascistas

  Scenario: Decisión de veto con políticas fascistas
    Given una estrategia fascista
    And una lista de políticas para veto: "fascist", "liberal"
    When la estrategia fascista decide sobre veto
    Then no debe proponer veto con fascistas

  Scenario: Aceptación de veto sin políticas fascistas
    Given una estrategia fascista
    And una lista de políticas para veto: "liberal", "communist"
    When la estrategia fascista decide aceptar veto
    Then debe aceptar veto sin fascistas

  Scenario: Rechazo de veto con políticas fascistas
    Given una estrategia fascista
    And una lista de políticas para veto: "fascist", "liberal"
    When la estrategia fascista decide aceptar veto
    Then no debe aceptar veto con fascistas

  Scenario: Ejecución de liberal conocido
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para ejecución
    And el jugador 2 es conocido como liberal
    When la estrategia fascista elige un jugador para ejecutar
    Then debe elegir el jugador liberal conocido
    And debe priorizar liberales para ejecución

  Scenario: Ejecución cuando liberales cerca de victoria
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para ejecución
    And el jugador 1 es conocido como liberal
    And los liberales están cerca de la victoria
    When la estrategia fascista elige un jugador para ejecutar
    Then debe priorizar eliminar liberales urgentemente

  Scenario: Inspección de no fascistas
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para inspección
    And el jugador 1 es fascista
    And el jugador 2 no es fascista
    When la estrategia fascista elige un jugador para inspeccionar
    Then debe elegir un jugador no fascista
    And no debe inspeccionar fascistas

  Scenario: Selección de fascista como próximo presidente
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para presidencia
    And el jugador 2 es fascista no Hitler
    When la estrategia fascista elige el siguiente presidente
    Then debe elegir el jugador fascista
    And debe priorizar fascistas para presidencia

  Scenario: Radicalización de liberal conocido
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para radicalización
    And el jugador 2 es conocido como liberal
    When la estrategia fascista elige un jugador para radicalizar
    Then debe elegir el jugador liberal conocido
    And debe convertir liberales en comunistas

  Scenario: Marcado de liberal para ejecución
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para marcado
    And el jugador 2 es conocido como liberal
    When la estrategia fascista elige un jugador para marcar
    Then debe elegir el jugador liberal conocido
    And debe usar mismo criterio que ejecución

  Scenario: Espionaje de no fascistas no inspeccionados
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para espionaje
    And el jugador 1 es fascista
    And el jugador 2 no fue inspeccionado
    When la estrategia fascista elige un jugador para espionar
    Then debe elegir un jugador no fascista no inspeccionado
    And debe obtener información útil

  Scenario: Decisión de propaganda con política liberal
    Given una estrategia fascista
    And una política liberal para propaganda
    When la estrategia fascista decide sobre propaganda
    Then debe descartar la política liberal en propaganda

  Scenario: Decisión de propaganda con política fascista
    Given una estrategia fascista
    And una política fascista para propaganda
    When la estrategia fascista decide sobre propaganda
    Then no debe descartar la política fascista

  Scenario: Selección de fascista como revelador
    Given una estrategia fascista
    And una lista de 3 jugadores elegibles para revelación
    And el jugador 2 es fascista
    When la estrategia fascista elige un revelador
    Then debe elegir el jugador fascista
    And debe revelar información a aliados

  Scenario: Perdón de Hitler marcado
    Given una estrategia fascista
    And Hitler está marcado para ejecución
    When la estrategia fascista decide sobre perdón
    Then debe perdonar a Hitler
    And siempre debe proteger a Hitler

  Scenario: Perdón de fascista marcado
    Given una estrategia fascista
    And un fascista está marcado para ejecución
    When la estrategia fascista decide sobre perdón
    Then debe perdonar al fascista
    And debe proteger a aliados fascistas

  Scenario: No perdón de liberal marcado
    Given una estrategia fascista
    And un liberal está marcado para ejecución
    When la estrategia fascista decide sobre perdón
    Then no debe perdonar al liberal
    And debe permitir ejecución de enemigos

  Scenario: Propuesta de veto sin fascistas como canciller
    Given una estrategia fascista
    And políticas sin fascistas para propuesta de veto
    When la estrategia fascista propone veto como canciller
    Then debe proponer veto sin opciones fascistas

  Scenario: Voto de no confianza con política fascista
    Given una estrategia fascista
    And una política fascista como última descartada
    When la estrategia fascista decide sobre voto de no confianza
    Then debe votar para promulgar la política fascista

  Scenario: Voto de no confianza con política liberal
    Given una estrategia fascista
    And una política liberal como última descartada
    When la estrategia fascista decide sobre voto de no confianza
    Then no debe votar para promulgar la política liberal

  Scenario: Remoción socialdemócrata priorizando comunistas
    Given una estrategia fascista
    And el estado tiene políticas comunistas y liberales
    When la estrategia fascista elige qué remover en poder socialdemócrata
    Then debe elegir remover del track comunista
    And debe debilitar a otros enemigos primero
