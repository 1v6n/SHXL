Feature: Gestión del flujo de juego en SHXLGame

  Como sistema de juego
  quiero inicializar correctamente el tablero, asignar jugadores, roles y fases,
  para garantizar que el juego de Secret Hitler XL se desarrolle según las reglas definidas.

  Background:
    Given a new SHXLGame instance

  Scenario: inicializar_el_tablero crea un GameBoard con los parámetros correctos
    When inicializo el tablero con 7 jugadores y flag comunista true
    Then se debe haber construido un GameBoard con state, 7, true
    And context.state.board debe asignarse al mock de GameBoard

  Scenario: elegir_primer_presidente asigna presidente de manera aleatoria
    Given el juego tiene active_players ["P0", "P1", "P2", "P3"]
    And randint returns 2
    When elijo primer presidente
    Then state.president_candidate debe ser "P2"

  Scenario: iniciar_juego ejecuta fases hasta game_over y devuelve el ganador
    Given current_phase execute returns itself once then sets game_over true
    And state.winner is "Fascists"
    When inicio el juego
    Then el ganador retornado debe ser "Fascists"
    And execute fue llamado al menos una vez sobre el objeto de fase

  Scenario: setup_game desactiva anti_policies si no hay comunistas y llama a los submétodos
    Given player_count 5
    And with_communists false
    And with_anti_policies true
    And with_emergency_powers false
    And human_player_indices [1,2]
    And ai_strategy is "random"
    And stubeo initialize_board, policy_deck_initialization, assign_players, inform_players, choose_first_president
    When configuro el juego
    Then game.player_count debe ser 5
    And game.communists_in_play debe ser false
    And game.anti_policies_in_play debe ser false
    And game.emergency_powers_in_play debe ser false
    And game.human_player_indices debe igualar [1,2]
    And game.ai_strategy debe ser "random"
    And initialize_board fue llamado una vez con argumentos (5, false)
    And policy_deck_initialization fue llamado una vez con el mock de PolicyFactory, false, false
    And assign_players fue llamado una vez
    And inform_players fue llamado una vez
    And choose_first_president fue llamado una vez
    And game.current_phase debe ser None

  Scenario: assign_players crea jugadores, asigna roles e identifica a Hitler
    Given un estado vacío con jugadores ["pA", "pB", "pC"]
    And parcheo PlayerFactory.create_players para agregar 3 mocks de jugador a state.players
    And parcheo RoleFactory.create_roles para retornar roles ["roleA", "roleB", "roleC"] donde roleB.is_hitler es true
    And parcheo PlayerFactory.update_player_strategies
    When llamo a assign_players
    Then PlayerFactory.create_players fue llamado una vez con (3, state, "smart", [])
    And RoleFactory.create_roles fue llamado una vez con (3, with_communists false)
    And cada mock-jugador obtuvo su atributo role asignado
    And hitler_player debe ser el mock-jugador cuyo is_hitler es true
    And PlayerFactory.update_player_strategies fue llamado una vez con (state.players, "smart")

  Scenario: inform_players informa fascistas y a Hitler en partidas de <8 jugadores
    Given state.players contiene:
      | id | is_fascist | is_hitler |
      | 0  | true       | false     |
      | 1  | true       | false     |
      | 2  | false      | true      |
      | 3  | false      | false     |
    And game.player_count is 7
    When llamo a inform_players
    Then cada fascista (id 0 y 1) debe tener .hitler asignado al mock de Hitler (id 2)
    And cada lista .fascists de los fascistas debe igualar la lista de otros mocks fascistas
    And el mock de Hitler debe tener .fascists igual a [fascista0, fascista1]

  Scenario: inform_players informa comunistas en partidas de <11 jugadores
    Given state.players contiene:
      | id | is_communist | is_fascist | is_hitler |
      | 0  | true         | false      | false     |
      | 1  | true         | false      | false     |
      | 2  | false        | true       | false     |
      | 3  | false        | false      | true      |
    And game.player_count is 10
    When llamo a inform_players
    Then cada .known_communists de los comunistas debe listar los IDs de los otros comunistas
      | id | known_communists |
      | 0  | [1]              |
      | 1  | [0]              |

  Scenario: inform_players no informa comunistas en partidas de ≥11 jugadores
    Given state.players contiene:
      | id | is_communist | is_fascist | is_hitler |
      | 0  | true         | false      | false     |
      | 1  | true         | false      | false     |
      | 2  | false        | true       | false     |
      | 3  | false        | false      | true      |
    And game.player_count is 11
    When llamo a inform_players
    Then ningún mock comunista debe tener el atributo .known_communists definido
