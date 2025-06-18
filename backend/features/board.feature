Feature: Configuración y funcionalidad del tablero de juego

  Como sistema de juego,
  quiero configurar automáticamente el tablero con las pistas de políticas y poderes correctos según el número de jugadores,
  para asegurar que el flujo del juego siga las reglas establecidas y los jugadores tengan la experiencia adecuada.

  Scenario Outline: Configuración inicial del tablero según número de jugadores
    Given una partida de <player_count> jugadores
    And la opción comunistas está <with_communists>
    When inicializo el tablero
    Then el tamaño de la pista liberal debe ser 5
    And el tamaño de la pista fascista debe ser 6
    And el tamaño de la pista comunista debe ser <communist_track_size>
    And los poderes fascistas deben ser <fascist_powers>
    And los poderes comunistas deben ser <communist_powers>

    Examples:
      | player_count | with_communists | communist_track_size | fascist_powers                                                       | communist_powers                                          |
      | 7            | true            | 5                    | [None, None, "policy_peek", "execution", "execution"]               | ["bugging", "radicalization", "five_year_plan", "congress"] |
      | 8            | true            | 5                    | [None, "investigate_loyalty", "special_election", "execution", "execution"] | ["bugging", "radicalization", "five_year_plan", "congress"] |
      | 9            | true            | 6                    | [None, "investigate_loyalty", "special_election", "execution", "execution"] | ["bugging", "radicalization", "five_year_plan", "congress", "confession"] |
      | 11           | true            | 6                    | ["investigate_loyalty", "investigate_loyalty", "special_election", "execution", "execution"] | [None, "radicalization", "five_year_plan", "radicalization", "confession"] |
      | 7            | false           | 0                    | [None, None, "policy_peek", "execution", "execution"]               | []                                                        |
      | 9            | false           | 0                    | [None, "investigate_loyalty", "special_election", "execution", "execution"] | []                                                        |

  Scenario Outline: Promulgación de políticas y progreso en las pistas
    Given una partida de <player_count> jugadores
    And la opción comunistas está <with_communists>
    And un tablero inicializado
    When promulgo <policy_count> políticas <policy_type>
    Then la pista <policy_type> debe tener <expected_track_value> políticas
    And el poder otorgado debe ser <expected_power>
    And el veto debe estar <veto_status>

    Examples:
      | player_count | with_communists | policy_count | policy_type | expected_track_value | expected_power        | veto_status  |
      | 7            | true            | 1            | liberal     | 1                    | None                  | no disponible |
      | 7            | true            | 3            | fascist     | 3                    | "policy_peek"         | no disponible |
      | 7            | true            | 5            | fascist     | 5                    | "execution"           | disponible   |
      | 9            | true            | 2            | communist   | 2                    | "radicalization"      | no disponible |
      | 9            | true            | 3            | fascist     | 3                    | "special_election"    | no disponible |

  Scenario Outline: Condiciones de victoria
    Given una partida de <player_count> jugadores
    And la opción comunistas está <with_communists>
    And un tablero inicializado
    When promulgo <policy_count> políticas <policy_type>
    Then el juego debe estar <game_status>
    And el ganador debe ser <winner>

    Examples:
      | player_count | with_communists | policy_count | policy_type | game_status | winner    |
      | 7            | true            | 5            | liberal     | terminado   | liberal   |
      | 7            | true            | 6            | fascist     | terminado   | fascist   |
      | 7            | true            | 5            | communist   | terminado   | communist |
      | 7            | false           | 5            | liberal     | terminado   | liberal   |
      | 7            | false           | 6            | fascist     | terminado   | fascist   |

  Scenario: Manejo del mazo de políticas - robar y descartar
    Given una partida de 7 jugadores
    And la opción comunistas está true
    And un tablero inicializado con mazo de políticas
    When robo 3 políticas
    Then debo tener 3 políticas en mano
    And el mazo debe tener menos políticas
    When descarto 1 política
    Then la pila de descartes debe tener 1 política

  Scenario: Redistribución del mazo cuando se agota
    Given una partida de 7 jugadores
    And la opción comunistas está true
    And un tablero inicializado con mazo de políticas
    And políticas en la pila de descartes
    When robo más políticas de las disponibles en el mazo
    Then el mazo debe reorganizarse incluyendo los descartes
    And debo poder robar las políticas solicitadas
