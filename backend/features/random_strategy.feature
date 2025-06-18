Feature: Funcionalidad de la estrategia aleatoria

  Como implementación de estrategia de jugador,
  quiero hacer decisiones aleatorias en todas las situaciones del juego,
  para proporcionar un comportamiento impredecible y variado.

  Scenario: Inicialización de estrategia aleatoria
    Given un jugador mock
    When creo una estrategia aleatoria con el jugador
    Then la estrategia debe estar inicializada correctamente
    And debe heredar de PlayerStrategy

  Scenario: Nominación aleatoria de canciller
    Given una estrategia aleatoria
    And una lista de 3 jugadores elegibles
    When la estrategia nomina un canciller
    Then debe retornar uno de los jugadores elegibles
    And el jugador seleccionado debe estar en la lista original

  Scenario: Filtrado aleatorio de políticas como presidente
    Given una estrategia aleatoria
    And una lista de 3 políticas: "liberal", "fascist", "communist"
    When la estrategia filtra las políticas
    Then debe retornar 2 políticas para pasar
    And debe retornar 1 política para descartar
    And las políticas filtradas deben ser del conjunto original

  Scenario: Selección aleatoria de política como canciller
    Given una estrategia aleatoria
    And una lista de 2 políticas: "liberal", "fascist"
    When la estrategia elige una política
    Then debe retornar una política para promulgar
    And debe retornar una política para descartar
    And ambas políticas deben ser del conjunto original

  Scenario: Votación aleatoria en gobierno
    Given una estrategia aleatoria
    And un presidente mock
    And un canciller mock
    When la estrategia vota en el gobierno
    Then debe retornar un valor booleano
    And el resultado debe ser aleatorio

  Scenario: Decisión aleatoria de veto
    Given una estrategia aleatoria
    And una lista de políticas para veto
    When la estrategia decide sobre veto
    Then debe retornar un valor booleano
    And debe tener baja probabilidad de veto

  Scenario: Aceptación aleatoria de veto
    Given una estrategia aleatoria
    And una propuesta de veto
    When la estrategia decide aceptar veto
    Then debe retornar un valor booleano
    And debe tener baja probabilidad de aceptación

  Scenario: Selección aleatoria para ejecución
    Given una estrategia aleatoria
    And una lista de 4 jugadores elegibles para ejecución
    When la estrategia elige un jugador para ejecutar
    Then debe retornar uno de los jugadores elegibles

  Scenario: Selección aleatoria para inspección
    Given una estrategia aleatoria
    And una lista de 3 jugadores elegibles para inspección
    When la estrategia elige un jugador para inspeccionar
    Then debe retornar uno de los jugadores elegibles

  Scenario: Selección aleatoria de siguiente presidente
    Given una estrategia aleatoria
    And una lista de 5 jugadores elegibles para presidencia
    When la estrategia elige el siguiente presidente
    Then debe retornar uno de los jugadores elegibles

  Scenario: Selección aleatoria para radicalización
    Given una estrategia aleatoria
    And una lista de 2 jugadores elegibles para radicalización
    When la estrategia elige un jugador para radicalizar
    Then debe retornar uno de los jugadores elegibles

  Scenario: Selección aleatoria para marcado
    Given una estrategia aleatoria
    And una lista de 3 jugadores elegibles para marcado
    When la estrategia elige un jugador para marcar
    Then debe retornar uno de los jugadores elegibles

  Scenario: Selección aleatoria para espionaje
    Given una estrategia aleatoria
    And una lista de 4 jugadores elegibles para espionaje
    When la estrategia elige un jugador para espionar
    Then debe retornar uno de los jugadores elegibles

  Scenario: Decisión aleatoria de propaganda
    Given una estrategia aleatoria
    And una política para decisión de propaganda
    When la estrategia decide sobre propaganda
    Then debe retornar un valor booleano
    And el resultado debe ser aleatorio

  Scenario: Selección aleatoria de revelador
    Given una estrategia aleatoria
    And una lista de 3 jugadores elegibles para revelación
    When la estrategia elige un revelador
    Then debe retornar uno de los jugadores elegibles

  Scenario: Decisión aleatoria de perdón
    Given una estrategia aleatoria
    When la estrategia decide sobre perdón
    Then debe retornar un valor booleano
    And el resultado debe ser aleatorio

  Scenario: Propuesta aleatoria de veto como canciller
    Given una estrategia aleatoria
    And políticas para propuesta de veto
    When la estrategia propone veto como canciller
    Then debe retornar un valor booleano
    And debe tener baja probabilidad de propuesta

  Scenario: Decisión aleatoria de voto de no confianza
    Given una estrategia aleatoria
    When la estrategia decide sobre voto de no confianza
    Then debe retornar un valor booleano
    And el resultado debe ser aleatorio

  Scenario: Selección aleatoria de remoción socialdemócrata
    Given una estrategia aleatoria
    When la estrategia elige qué remover en poder socialdemócrata
    Then la elección de remoción debe retornar "fascist" o "communist"
    And el resultado debe estar en las opciones válidas

  Scenario: Comportamiento consistente con semilla aleatoria
    Given una estrategia aleatoria con semilla fija
    And una lista de jugadores elegibles
    When la estrategia hace múltiples decisiones
    Then debe mostrar variabilidad en los resultados
    And debe respetar las probabilidades configuradas

  Scenario: Manejo de listas vacías
    Given una estrategia aleatoria
    When la estrategia intenta elegir de una lista vacía
    Then debe manejar el error apropiadamente
    And no debe causar una excepción no controlada
