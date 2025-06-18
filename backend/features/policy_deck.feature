Feature: Generación del mazo de políticas según reglas y configuraciones

  Como sistema de juego,
  quiero construir automáticamente el mazo de cartas de políticas con la cantidad y tipo correctos para cada partido,
  para asegurar que el desarrollo de la partida refleje las condiciones iniciales establecidas.

  Scenario Outline: Generar mazo de políticas en distintas configuraciones
    Given una partida de <player_count> jugadores
    And la opción comunistas está <with_communists>
    And la opción anti-policies está <with_anti_policies>
    And la opción poderes de emergencia está <with_emergency_powers>
    When genero el mazo de políticas
    Then el mazo debe contener <liberales> cartas liberales
    And <fascistas> cartas fascistas
    And <comunistas> cartas comunistas
    And <antifascistas> cartas anti-fascistas
    And <anticomunistas> cartas anti-comunistas
    And <socialdemocratas> cartas socialdemócratas
    And <article48> cartas Article 48
    And <enablingact> cartas Enabling Act

    Examples:
      | player_count | with_communists | with_anti_policies | with_emergency_powers | liberales | fascistas | comunistas | antifascistas | anticomunistas | socialdemocratas | article48 | enablingact |
      | 7            | true            | false              | false                 | 5         | 10        | 8          | 0             | 0              | 0                | 0         | 0           |
      | 9            | true            | true               | false                 | 5         | 8         | 7          | 1             | 1              | 1                | 0         | 0           |
      | 11           | true            | false              | true                  | 6         | 9         | 8          | 0             | 0              | 0                | 1         | 0           |
      | 14           | true            | true               | true                  | 5         | 8         | 7          | 1             | 1              | 1                | 1         | 1           |
      | 6            | false           | false              | false                 | 5         | 10        | 0          | 0             | 0              | 0                | 0         | 0           |
