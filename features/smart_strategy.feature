# filepath: c:\Users\Admin\Documents\MEGA\Facultad\Materias\IngSoft\SHXL\features\smart_strategy.feature
Feature: Funcionalidad de la estrategia inteligente

  Como implementación de estrategia de jugador inteligente,
  quiero tomar decisiones estratégicas avanzadas basadas en mi rol y estado del juego,
  para maximizar las posibilidades de victoria adaptándome a diferentes escenarios.

  Scenario: Inicialización de estrategia inteligente
    Given un jugador smart mock
    When creo una estrategia smart con el jugador
    Then la estrategia smart debe estar inicializada correctamente
    And la estrategia smart debe heredar de PlayerStrategy

  # Fascist nomination scenarios
  Scenario: Nominación fascista - Hitler canciller cuando es posible
    Given una estrategia smart fascista
    And una lista de 3 jugadores elegibles para canciller
    And el jugador 2 es Hitler elegible
    And el estado del juego tiene 3 políticas fascistas
    When la estrategia smart nomina un canciller
    Then debe retornar a Hitler como canciller

  Scenario: Nominación fascista - Fascista como canciller cuando Hitler no disponible
    Given una estrategia smart fascista
    And una lista de 3 jugadores elegibles para canciller
    And el jugador 2 es fascista no Hitler
    And el jugador 3 es liberal
    When la estrategia smart nomina un canciller
    Then debe retornar el jugador fascista conocido

  # Liberal nomination scenarios
  Scenario: Nominación liberal - Priorizando liberales conocidos
    Given una estrategia smart liberal
    And una lista de 4 jugadores elegibles para canciller
    And el jugador 2 es conocido como liberal
    And el jugador 3 es conocido como fascista
    When la estrategia smart nomina un canciller
    Then debe retornar el jugador liberal conocido
    And no debe elegir el jugador fascista conocido

  Scenario: Nominación liberal - Evitando jugadores sospechosos
    Given una estrategia smart liberal
    And una lista de 3 jugadores elegibles para canciller
    And el jugador 1 tiene historial de políticas fascistas
    And el jugador 2 no tiene historial sospechoso
    When la estrategia smart nomina un canciller
    Then debe retornar el jugador sin historial sospechoso

  # Policy filtering scenarios
  Scenario: Filtrado fascista - Priorizando políticas fascistas
    Given una estrategia smart fascista
    And una lista de 3 políticas: "fascist", "liberal", "communist"
    When la estrategia smart filtra las políticas
    Then debe mantener la política fascista
    And debe descartar la política liberal
    And debe retornar 2 políticas para pasar

  Scenario: Filtrado liberal - Priorizando políticas liberales
    Given una estrategia smart liberal
    And una lista de 3 políticas: "liberal", "fascist", "communist"
    When la estrategia smart filtra las políticas
    Then debe mantener la política liberal
    And debe descartar la política fascista
    And debe retornar 2 políticas para pasar

  Scenario: Filtrado comunista - Priorizando políticas comunistas
    Given una estrategia smart comunista
    And una lista de 3 políticas: "communist", "fascist", "liberal"
    When la estrategia smart filtra las políticas
    Then debe mantener la política comunista
    And debe descartar la política liberal
    And debe retornar 2 políticas para pasar

  # Policy choice scenarios
  Scenario: Selección fascista - Eligiendo política fascista
    Given una estrategia smart fascista
    And una lista de 2 políticas: "fascist", "liberal"
    When la estrategia smart elige una política
    Then debe promulgar la política fascista
    And debe descartar la política liberal

  Scenario: Selección liberal - Eligiendo política liberal
    Given una estrategia smart liberal
    And una lista de 2 políticas: "liberal", "fascist"
    When la estrategia smart elige una política
    Then debe promulgar la política liberal
    And debe descartar la política fascista

  Scenario: Selección comunista - Eligiendo política comunista
    Given una estrategia smart comunista
    And una lista de 2 políticas: "communist", "liberal"
    When la estrategia smart elige una política
    Then debe promulgar la política comunista
    And debe descartar la política liberal

  # Voting scenarios
  Scenario: Votación fascista - Apoyando gobierno fascista
    Given una estrategia smart fascista
    And un presidente smart fascista
    And un canciller smart fascista
    When la estrategia smart vota en el gobierno
    Then debe votar positivamente

  Scenario: Votación fascista - Apoyando Hitler cuando es seguro
    Given una estrategia smart fascista
    And un presidente smart cualquiera
    And un canciller smart que es Hitler
    And el estado del juego tiene 3 políticas fascistas
    When la estrategia smart vota en el gobierno
    Then debe votar positivamente

  Scenario: Votación liberal - Rechazando fascistas conocidos
    Given una estrategia smart liberal
    And un presidente smart cualquiera
    And un canciller smart conocido como fascista
    When la estrategia smart vota en el gobierno
    Then debe votar negativamente

  Scenario: Votación liberal - Cautelosa en situación peligrosa
    Given una estrategia smart liberal
    And un presidente smart sin información
    And un canciller smart sin información
    And el estado del juego tiene 4 políticas fascistas
    When la estrategia smart vota en el gobierno
    Then el voto debe ser muy cauteloso

  Scenario: Votación comunista - Favoreciendo el caos con fascistas
    Given una estrategia smart comunista
    And un presidente smart cualquiera
    And un canciller smart conocido como fascista
    When la estrategia smart vota en el gobierno
    Then el voto debe tender a ser positivo para crear caos

  # Veto scenarios
  Scenario: Veto liberal - Vetando políticas fascistas
    Given una estrategia smart liberal
    And una lista de políticas para veto: "fascist", "fascist"
    When la estrategia smart decide sobre veto
    Then debe proponer veto

  Scenario: Veto fascista - Vetando políticas liberales
    Given una estrategia smart fascista
    And una lista de políticas para veto: "liberal", "liberal"
    When la estrategia smart decide sobre veto
    Then debe proponer veto

  Scenario: Veto comunista - Vetando cuando no hay comunistas
    Given una estrategia smart comunista
    And una lista de políticas para veto: "liberal", "liberal"
    When la estrategia smart decide sobre veto
    Then debe proponer veto

  # Accept veto scenarios
  Scenario: Aceptar veto con tracker de elección alto
    Given una estrategia smart liberal
    And una lista de políticas para veto: "fascist", "fascist"
    And el tracker de elección está en 2
    When la estrategia smart decide aceptar veto
    Then debe aceptar el veto solo en situaciones críticas

  # Execution scenarios
  Scenario: Ejecución liberal - Matando fascistas conocidos
    Given una estrategia smart liberal
    And una lista de 3 jugadores elegibles para ejecución
    And el jugador 2 es conocido como fascista
    When la estrategia smart elige un jugador para ejecutar
    Then debe elegir el jugador fascista conocido

  Scenario: Ejecución comunista - Priorizando fascistas
    Given una estrategia smart comunista
    And una lista de 3 jugadores elegibles para ejecución
    And el jugador 1 es conocido como fascista
    And el jugador 2 es conocido como liberal
    When la estrategia smart elige un jugador para ejecutar
    Then debe elegir el jugador fascista conocido

  # Inspection scenarios
  Scenario: Inspección - Priorizando jugadores no inspeccionados
    Given una estrategia smart cualquier rol
    And una lista de 3 jugadores elegibles para inspección
    And el jugador 1 ya fue inspeccionado
    And el jugador 2 no fue inspeccionado
    When la estrategia smart elige un jugador para inspeccionar
    Then debe elegir un jugador no inspeccionado

  # Special election scenarios
  Scenario: Elección especial fascista - Eligiendo fascistas
    Given una estrategia smart fascista
    And una lista de 3 jugadores elegibles para presidencia especial
    And el jugador 2 es fascista
    When la estrategia smart elige el siguiente presidente
    Then debe elegir el jugador fascista

  Scenario: Elección especial liberal - Eligiendo liberales conocidos
    Given una estrategia smart liberal
    And una lista de 3 jugadores elegibles para presidencia especial
    And el jugador 2 es conocido como liberal
    When la estrategia smart elige el siguiente presidente
    Then debe elegir el jugador liberal conocido

  # Propaganda scenarios
  Scenario: Propaganda fascista - Descartando política liberal
    Given una estrategia smart fascista
    And una política liberal para propaganda
    When la estrategia smart decide sobre propaganda
    Then debe descartar la política liberal

  Scenario: Propaganda liberal - Descartando política fascista
    Given una estrategia smart liberal
    And una política fascista para propaganda
    When la estrategia smart decide sobre propaganda
    Then debe descartar la política fascista

  Scenario: Propaganda - Conservando cartas de poder de emergencia
    Given una estrategia smart cualquier rol
    And una política article48 para propaganda
    When la estrategia smart decide sobre propaganda
    Then no debe descartar la carta de poder

  # Revealer scenarios
  Scenario: Revelación fascista - Eligiendo fascista para revelar
    Given una estrategia smart fascista
    And una lista de 3 jugadores elegibles para revelación
    And el jugador 2 es fascista
    When la estrategia smart elige un revelador
    Then debe elegir el jugador fascista

  # Mark for execution scenarios
  Scenario: Marcado liberal - Priorizando Hitler conocido
    Given una estrategia smart liberal
    And una lista de 3 jugadores elegibles para marcado
    And el jugador 2 es conocido como fascista y es Hitler
    When la estrategia smart elige un jugador para marcar
    Then debe elegir a Hitler conocido

  # Pardon scenarios
  Scenario: Perdón fascista - Perdonando a Hitler
    Given una estrategia smart fascista
    And un jugador Hitler marcado para ejecución
    When la estrategia smart decide sobre perdón
    Then debe perdonar a Hitler

  Scenario: Perdón liberal - Perdonando liberal conocido
    Given una estrategia smart liberal
    And un jugador liberal conocido marcado para ejecución
    When la estrategia smart decide sobre perdón
    Then debe perdonar al jugador liberal

  # Social democratic removal scenarios
  Scenario: Remoción socialdemócrata fascista - Removiendo track liberal
    Given una estrategia smart fascista
    When la estrategia smart elige qué remover en poder socialdemócrata
    Then debe elegir remover del track liberal

  Scenario: Remoción socialdemócrata liberal - Removiendo track fascista
    Given una estrategia smart liberal
    When la estrategia smart elige qué remover en poder socialdemócrata
    Then debe elegir remover del track fascista

  # Vote of no confidence scenarios
  Scenario: Voto de no confianza - Promulgando política del propio bando
    Given una estrategia smart liberal
    And una política liberal como última descartada
    When la estrategia smart decide sobre voto de no confianza
    Then debe votar para promulgar la política liberal

  Scenario: Voto de no confianza - Rechazando política enemiga
    Given una estrategia smart liberal
    And una política fascista como última descartada
    When la estrategia smart decide sobre voto de no confianza
    Then no debe votar para promulgar la política fascista
