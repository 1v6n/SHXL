Feature: Fase de Elección - Nominación y Votación

  Como participante en una partida de Secret Hitler XL,
  quiero que la fase de elección funcione correctamente con nominación de canciller y votación de gobierno,
  para que el proceso democrático del juego se desarrolle según las reglas establecidas.

  Background:
    Given una partida de Secret Hitler XL con jugadores activos

  # =============================================================================
  # NOMINACIÓN DE CANCILLER
  # =============================================================================

  Scenario Outline: El presidente nomina correctamente a un candidato elegible
    Given el presidente en turno es el jugador <presidente>
    And el último presidente electo fue el jugador <ultimo_presidente>
    And el último canciller electo fue el jugador <ultimo_canciller>
    And hay <numero_jugadores> jugadores activos
    When el presidente nomina como canciller al jugador <candidato>
    Then la nominación es <validez>
    And la lista de candidatos elegibles contiene a <esperados>

    Examples:
      | presidente | ultimo_presidente | ultimo_canciller | numero_jugadores | candidato | validez     | esperados                 |
      | 1          | 2                 | 3                | 8                | 4         | válida      | todos excepto 1, 2, 3     |
      | 1          | 2                 | 3                | 8                | 2         | inválida    | todos excepto 1, 2, 3     |
      | 1          | 2                 | 3                | 7                | 3         | válida      | todos excepto 1, 2        |
      | 1          | 2                 | 3                | 7                | 2         | inválida    | todos excepto 1, 2        |

  Scenario: No hay candidatos elegibles tras tres elecciones fallidas (chaos policy)
    Given se han realizado tres elecciones fallidas consecutivas
    When el presidente intenta nominar un candidato a canciller
    Then la lista de candidatos elegibles está vacía
    And se promulga automáticamente una policy de caos

  Scenario: Nominación válida tanto en partidas con humanos como con bots
    Given la partida contiene jugadores humanos y bots
    And el último presidente electo fue el jugador 2
    And el último canciller electo fue el jugador 3
    When el presidente nomina como canciller a un bot elegible
    Then la nominación es válida

  Scenario: Si hay menos o igual a 7 jugadores, solo el último presidente queda vetado
    Given hay 7 jugadores activos
    And el último presidente electo fue el jugador 4
    And el último canciller electo fue el jugador 5
    When el presidente intenta nominar como canciller al jugador 5
    Then la nominación es válida
    And la lista de candidatos elegibles contiene a todos excepto el presidente y el último presidente

  Scenario: Si hay más de 7 jugadores, último presidente y último canciller quedan vetados
    Given hay 8 jugadores activos
    And el último presidente electo fue el jugador 4
    And el último canciller electo fue el jugador 5
    When el presidente intenta nominar como canciller al jugador 4
    Then la nominación es inválida
    When el presidente intenta nominar como canciller al jugador 5
    Then la nominación es inválida

  # =============================================================================
  # VOTACIÓN DE GOBIERNO
  # =============================================================================

  Scenario: Votación exitosa - gobierno aprobado por mayoría
    Given el presidente en turno es el jugador 1
    And el presidente ha nominado como canciller al jugador 3
    And los jugadores votan de la siguiente manera:
      | jugador | voto |
      | 1       | Ja   |
      | 2       | Ja   |
      | 3       | Ja   |
      | 4       | Ja   |
      | 5       | Ja   |
      | 6       | Nein |
      | 7       | Nein |
      | 8       | Nein |
    When se procesan los votos
    Then el gobierno es aprobado
    And el jugador 1 se convierte en presidente oficial
    And el jugador 3 se convierte en canciller oficial
    And el tracker de elecciones fallidas se reinicia a 0
    And la partida avanza a la fase legislativa

  Scenario: Votación fallida - gobierno rechazado por mayoría
    Given el presidente en turno es el jugador 1
    And el presidente ha nominado como canciller al jugador 3
    And los jugadores votan de la siguiente manera:
      | jugador | voto |
      | 1       | Ja   |
      | 2       | Ja   |
      | 3       | Nein |
      | 4       | Nein |
      | 5       | Nein |
      | 6       | Nein |
      | 7       | Nein |
      | 8       | Nein |
    When se procesan los votos
    Then el gobierno es rechazado
    And el tracker de elecciones fallidas se incrementa en 1
    And el siguiente jugador se convierte en candidato a presidente
    And la partida permanece en la fase de elección

  Scenario: Votación empatada - gobierno rechazado
    Given hay 6 jugadores activos
    And el presidente ha nominado como canciller al jugador 3
    And los jugadores votan de la siguiente manera:
      | jugador | voto |
      | 1       | Ja   |
      | 2       | Ja   |
      | 3       | Ja   |
      | 4       | Nein |
      | 5       | Nein |
      | 6       | Nein |
    When se procesan los votos
    Then el gobierno es rechazado
    And el tracker de elecciones fallidas se incrementa en 1

  Scenario: Tercera elección fallida consecutiva - chaos policy
    Given el tracker de elecciones fallidas está en 2
    And el presidente ha nominado como canciller al jugador 3
    And los jugadores votan de la siguiente manera:
      | jugador | voto |
      | 1       | Ja   |
      | 2       | Nein |
      | 3       | Nein |
      | 4       | Nein |
      | 5       | Nein |
      | 6       | Nein |
      | 7       | Nein |
      | 8       | Nein |
    When se procesan los votos
    Then el gobierno es rechazado
    And el tracker de elecciones fallidas llega a 3
    And se promulga automáticamente una policy de caos
    And el tracker de elecciones fallidas se reinicia a 0
    And se reinician los límites de términos

  Scenario: Hitler elegido canciller con 3+ políticas fascistas - victoria fascista
    Given hay 4 políticas fascistas promulgadas
    And el jugador 3 es Hitler para votación
    And el presidente ha nominado como canciller al jugador 3
    And los jugadores votan de la siguiente manera:
      | jugador | voto |
      | 1       | Ja   |
      | 2       | Ja   |
      | 3       | Ja   |
      | 4       | Ja   |
      | 5       | Ja   |
      | 6       | Nein |
      | 7       | Nein |
      | 8       | Nein |
    When se procesan los votos
    Then el gobierno es aprobado
    And los fascistas ganan la partida
    And el juego termina

  Scenario: Votación con jugadores humanos
    Given hay jugadores humanos en la partida
    And el presidente ha nominado como canciller al jugador 3
    When inicia la votación
    Then el sistema solicita el voto de cada jugador humano
    And los bots votan automáticamente según su estrategia

  Scenario: Votación con solo bots
    Given todos los jugadores son bots
    And el presidente ha nominado como canciller al jugador 3
    When inicia la votación
    Then todos los jugadores votan automáticamente según su estrategia
    And se procesan los votos inmediatamente

  Scenario Outline: Diferentes resultados de votación según número de jugadores
    Given hay <jugadores> jugadores activos
    And el presidente ha nominado como canciller al jugador 3
    And <votos_ja> jugadores votan "Ja"
    And <votos_nein> jugadores votan "Nein"
    When se procesan los votos
    Then el gobierno es <resultado>

    Examples:
      | jugadores | votos_ja | votos_nein | resultado  |
      | 5         | 3        | 2          | aprobado   |
      | 5         | 2        | 3          | rechazado  |
      | 6         | 3        | 3          | rechazado  |
      | 7         | 4        | 3          | aprobado   |
      | 8         | 4        | 4          | rechazado  |
      | 9         | 5        | 4          | aprobado   |
      | 10        | 5        | 5          | rechazado  |

  Scenario: Mostrar resultados de votación individual
    Given el presidente ha nominado como canciller al jugador 3
    And los jugadores votan de la siguiente manera:
      | jugador | voto |
      | 1       | Ja   |
      | 2       | Nein |
      | 3       | Ja   |
      | 4       | Nein |
      | 5       | Ja   |
      | 6       | Nein |
      | 7       | Ja   |
      | 8       | Nein |
    When se procesan los votos
    And se muestran los resultados de votación
    Then se muestra que el jugador 1 votó "Ja"
    And se muestra que el jugador 2 votó "Nein"
    And se muestra el resultado final como "empate - gobierno rechazado"

  Scenario: Votación con jugador marcado para ejecución
    Given una partida de Secret Hitler XL con jugadores activos
    And el jugador 5 está marcado para ejecución
    And han pasado 3 políticas fascistas desde el marcado
    And el presidente ha nominado como canciller al jugador 3
    When inicia la votación
    Then el jugador 5 es ejecutado antes de la votación
    And el jugador 5 no participa en la votación
    And los jugadores restantes votan de la siguiente manera:
      | jugador | voto |
      | 1       | Ja   |
      | 2       | Ja   |
      | 3       | Ja   |
      | 4       | Nein |
      | 6       | Nein |
      | 7       | Nein |
      | 8       | Nein |
    And los jugadores restantes proceden a votar
