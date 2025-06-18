Feature: Funcionalidad del estado de juego

  Como sistema de juego,
  quiero gestionar correctamente el estado del juego incluyendo jugadores, rotación de presidencia, y trackers,
  para asegurar que el flujo del juego siga las reglas establecidas.  Scenario: Inicialización del estado de juego
    Given un estado de juego nuevo
    Then el juego debe estar en curso
    And el ganador debe ser None
    And el tracker de elecciones debe ser 0
    And la lista de jugadores debe estar vacía

  Scenario: Agregar jugadores al juego
    Given un estado de juego nuevo
    When agrego 5 jugadores al estado de juego
    Then debe haber 5 jugadores en total
    And debe haber 5 jugadores activos
    And todos los jugadores deben estar vivos

  Scenario: Verificar candidatos elegibles para canciller
    Given un estado de juego con 5 jugadores
    And el jugador 0 es el candidato a presidente
    And el jugador 1 está en la lista de term-limited
    When verifico los candidatos elegibles para canciller
    Then deben haber 3 candidatos elegibles
    And el jugador 0 no debe ser elegible
    And el jugador 1 no debe ser elegible

  Scenario: Rotación normal de presidencia
    Given un estado de juego con 5 jugadores
    And el jugador 2 es el presidente actual
    When calculo el siguiente presidente
    Then el siguiente presidente debe ser el jugador 3

  Scenario: Rotación de presidencia con jugador muerto
    Given un estado de juego con 5 jugadores
    And el jugador 2 es el presidente actual
    And el jugador 3 está muerto
    When calculo el siguiente presidente
    Then el siguiente presidente debe ser el jugador 4
    And debe haber 4 jugadores activos

  Scenario: Muerte del presidente actual
    Given un estado de juego con 5 jugadores
    And el jugador 2 es el presidente actual
    When el jugador 2 muere
    Then el jugador 2 debe estar muerto
    And debe haber 4 jugadores activos
    And el siguiente candidato a presidente debe ser establecido

  Scenario: Incrementar tracker de elecciones
    Given un estado de juego nuevo
    When incremento el tracker de elecciones
    Then el tracker de elecciones debe ser 1
    When incremento el tracker de elecciones
    Then el tracker de elecciones debe ser 2

  Scenario: Resetear tracker de elecciones
    Given un estado de juego nuevo
    And el tracker de elecciones es 2
    When reseteo el tracker de elecciones
    Then el tracker de elecciones debe ser 0
  Scenario: Actualizar trackers de políticas
    Given un estado de juego nuevo
    When incremento la pista liberal
    Then la pista liberal debe tener 1 políticas
    When incremento la pista fascista 2 veces
    Then la pista fascista debe tener 2 políticas
    When incremento la pista comunista
    Then la pista comunista debe tener 1 políticas
  Scenario: Configuración de veto disponible
    Given un estado de juego nuevo
    When establezco el veto como disponible
    Then el veto debe estar disponible

  Scenario: Investigación de jugadores
    Given un estado de juego con 3 jugadores
    When investigo al jugador 1
    Then el jugador 1 debe estar en la lista de investigados
    And la lista de investigados debe tener 1 jugador

  Scenario: Marcar jugador para ejecución
    Given un estado de juego con 3 jugadores
    When marco al jugador 2 para ejecución
    Then el jugador 2 debe estar marcado para ejecución
    And la lista de marcados para ejecución debe tener 1 jugador

  Scenario: Elección especial
    Given un estado de juego con 5 jugadores
    And el jugador 2 es el presidente actual
    When inicio una elección especial con retorno al índice 2
    Then debe estar en elección especial
    And el índice de retorno debe ser 2

  Scenario: Retorno de elección especial
    Given un estado de juego con 5 jugadores
    And el jugador 2 es el presidente actual
    And estoy en elección especial con retorno al índice 1
    When calculo el siguiente presidente
    Then el siguiente presidente debe ser el jugador 2
    And no debe estar en elección especial

  Scenario: Gestión de afiliaciones reveladas
    Given un estado de juego con 3 jugadores
    When revelo que el jugador 1 es fascist
    Then la afiliación del jugador 1 debe ser fascist
    When revelo que el jugador 2 es liberal
    Then la afiliación del jugador 2 debe ser liberal
