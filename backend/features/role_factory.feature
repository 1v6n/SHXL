Feature: Generación de roles según reglas y configuraciones

  Como sistema de juego,
  quiero asignar automáticamente los roles correctos según el número de jugadores y configuraciones,
  para asegurar que cada partida tenga la distribución de roles apropiada según las reglas del juego.

  Scenario Outline: Generar roles en distintas configuraciones
    Given una partida de <player_count> jugadores
    And la opción comunistas está <with_communists>
    When genero los roles
    Then la distribución debe contener <liberales> roles liberales
    And <fascistas> roles fascistas
    And <comunistas> roles comunistas
    And <hitler> roles Hitler
    And el total de roles debe ser <player_count>

    Examples:
      | player_count | with_communists | liberales | fascistas | comunistas | hitler |
      | 6            | true            | 3         | 1         | 1          | 1      |
      | 7            | true            | 4         | 1         | 1          | 1      |
      | 8            | true            | 4         | 2         | 1          | 1      |
      | 9            | true            | 4         | 2         | 2          | 1      |
      | 10           | true            | 5         | 2         | 2          | 1      |
      | 11           | true            | 5         | 3         | 2          | 1      |
      | 12           | true            | 6         | 3         | 2          | 1      |
      | 13           | true            | 6         | 3         | 3          | 1      |
      | 14           | true            | 7         | 3         | 3          | 1      |
      | 15           | true            | 7         | 4         | 3          | 1      |
      | 16           | true            | 7         | 4         | 4          | 1      |
      | 6            | false           | 4         | 1         | 0          | 1      |
      | 7            | false           | 4         | 2         | 0          | 1      |
      | 8            | false           | 5         | 2         | 0          | 1      |
      | 9            | false           | 5         | 3         | 0          | 1      |
      | 10           | false           | 6         | 3         | 0          | 1      |
      | 11           | false           | 6         | 4         | 0          | 1      |
      | 12           | false           | 7         | 4         | 0          | 1      |
      | 13           | false           | 7         | 5         | 0          | 1      |
      | 14           | false           | 8         | 5         | 0          | 1      |
      | 15           | false           | 8         | 6         | 0          | 1      |
      | 16           | false           | 9         | 6         | 0          | 1      |
