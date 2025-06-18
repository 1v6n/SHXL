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
    And state.winner is "fascist"
    When inicio el juego
    Then el ganador retornado debe ser "fascist"
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
    And game.current_phase debe ser SetupPhase

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

  Scenario: advance_turn incrementa el número de ronda y asigna próximo presidente
    Given state.round_number is 5
    And un mock de set_next_president es configurado
    When llamo a advance_turn
    Then state.round_number debe ser 6
    And set_next_president fue llamado una vez
    And el resultado debe ser state.president_candidate

  Scenario: nominate_chancellor retorna candidato seleccionado por el presidente
    Given state tiene president_candidate mock con nominate_chancellor
    And state tiene eligible_chancellors ["C1", "C2", "C3"]
    When llamo a nominate_chancellor
    Then president_candidate.nominate_chancellor fue llamado con eligible_chancellors
    And el resultado debe ser el candidato seleccionado

  Scenario: nominate_chancellor retorna None si no hay candidatos elegibles
    Given state.get_eligible_chancellors retorna lista vacía
    When llamo a nominate_chancellor
    Then el resultado debe ser None

  Scenario: vote_on_government cuenta votos y retorna resultado
    Given active_players con votes [true, true, false, true, false]
    When llamo a vote_on_government
    Then cada jugador.vote fue llamado una vez
    And state.last_votes debe igualar [true, true, false, true, false]
    And el resultado debe ser true (mayoría ja)
    And state.election_tracker debe ser 0

  Scenario: vote_on_government falla con mayoría nein
    Given active_players con votes [false, false, true]
    When llamo a vote_on_government
    Then el resultado debe ser false
    And state.election_tracker no debe cambiar

  Scenario: enact_chaos_policy promulga política del tope y resetea tracker
    Given board.draw_policy(1) retorna [mock_policy con type "fascist"]
    And state.enacted_policies is 3
    When llamo a enact_chaos_policy
    Then board.enact_policy fue llamado con mock_policy y chaos=true
    And state.election_tracker debe ser 0
    And state.enacted_policies debe ser 4
    And el resultado debe ser "fascist"

  Scenario: check_policy_win detecta victoria liberal
    Given board.liberal_track is 5
    And board.liberal_track_size is 5
    When llamo a check_policy_win
    Then state.game_over debe ser true
    And state.winner debe ser "liberal"
    And el resultado debe ser true

  Scenario: check_policy_win detecta victoria fascista
    Given board.fascist_track is 6
    And board.fascist_track_size is 6
    When llamo a check_policy_win
    Then state.game_over debe ser true
    And state.winner debe ser "fascist"
    And el resultado debe ser true

  Scenario: check_policy_win detecta victoria comunista
    Given communists_in_play is true
    And board.communist_track is 5
    And board.communist_track_size is 5
    When llamo a check_policy_win
    Then state.game_over debe ser true
    And state.winner debe ser "communist"
    And el resultado debe ser true

  Scenario: check_policy_win retorna false si no hay victorias
    Given board tracks no alcanzan sus tamaños máximos
    When llamo a check_policy_win
    Then state.game_over debe ser false
    And state.winner debe ser None
    And el resultado debe ser false

  Scenario: presidential_policy_choice filtra políticas y guarda descartada
    Given state.president mock con filter_policies retornando (chosen_policies, discarded_policy)
    When llamo a presidential_policy_choice con [pol1, pol2, pol3]
    Then president.filter_policies fue llamado con [pol1, pol2, pol3]
    And state.last_discarded debe ser discarded_policy
    And el resultado debe ser (chosen_policies, discarded_policy)

  Scenario: chancellor_propose_veto retorna false si veto no disponible
    Given board.veto_available is false
    When llamo a chancellor_propose_veto
    Then el resultado debe ser false

  Scenario: chancellor_propose_veto consulta al canciller si veto disponible
    Given board.veto_available is true
    And state.chancellor mock con veto() retornando true
    When llamo a chancellor_propose_veto
    Then chancellor.veto fue llamado
    And el resultado debe ser true

  Scenario: president_veto_accepted consulta al presidente sobre aceptar veto
    Given state.president mock con accept_veto() retornando false
    When llamo a president_veto_accepted
    Then president.accept_veto fue llamado
    And el resultado debe ser false

  Scenario: chancellor_policy_choice elige política y guarda descartada
    Given state.chancellor mock con choose_policy retornando (chosen, discarded)
    When llamo a chancellor_policy_choice con [pol1, pol2]
    Then chancellor.choose_policy fue llamado con [pol1, pol2]
    And state.last_discarded debe ser discarded
    And el resultado debe ser (chosen, discarded)

  Scenario: get_fascist_power retorna None si próximo poder está bloqueado
    Given state.block_next_fascist_power is true
    When llamo a get_fascist_power
    Then state.block_next_fascist_power debe ser false
    And el resultado debe ser None

  Scenario: get_fascist_power consulta board si no está bloqueado
    Given state.block_next_fascist_power is false
    And board.get_power_for_track_position retorna "investigation"
    When llamo a get_fascist_power
    Then board.get_power_for_track_position fue llamado con ("fascist", board.fascist_track)
    And el resultado debe ser "investigation"

  Scenario: get_communist_power retorna None si próximo poder está bloqueado
    Given state.block_next_communist_power is true
    When llamo a get_communist_power
    Then state.block_next_communist_power debe ser false
    And el resultado debe ser None

  Scenario: get_communist_power consulta board si no está bloqueado
    Given state.block_next_communist_power is false
    And board.get_power_for_track_position retorna "bugging"
    When llamo a get_communist_power
    Then board.get_power_for_track_position fue llamado con ("communist", board.communist_track)
    And el resultado debe ser "bugging"

  Scenario: execute_power delega a execute_presidential_power para poderes presidenciales
    Given PowerRegistry.get_owner("investigation") retorna PRESIDENT
    And execute_presidential_power mock retorna "investigation_result"
    When llamo a execute_power con "investigation"
    Then execute_presidential_power fue llamado con "investigation"
    And el resultado debe ser "investigation_result"

  Scenario: execute_power delega a execute_chancellor_power para poderes del canciller
    Given PowerRegistry.get_owner("chancellor_propaganda") retorna CHANCELLOR
    And execute_chancellor_power mock retorna "propaganda_result"
    When llamo a execute_power con "chancellor_propaganda"
    Then execute_chancellor_power fue llamado con "chancellor_propaganda"
    And el resultado debe ser "propaganda_result"

  Scenario: execute_presidential_power ejecuta investigación de lealtad
    Given PowerRegistry.get_power("investigate_loyalty", game) retorna mock_power
    And state.active_players contiene [president, player1, player2]
    And president.choose_player_to_investigate retorna player1
    And mock_power.execute(player1) retorna "liberal"
    When llamo a execute_presidential_power con "investigate_loyalty"
    Then president.choose_player_to_investigate fue llamado con [player1, player2]
    And mock_power.execute fue llamado con player1
    And el resultado debe ser "liberal"

  Scenario: execute_chancellor_power ejecuta propaganda del canciller
    Given PowerRegistry.get_power("chancellor_propaganda", game) retorna mock_power
    And mock_power.execute() retorna viewed_policy
    When llamo a execute_chancellor_power con "chancellor_propaganda"
    Then mock_power.execute fue llamado sin argumentos
    And el resultado debe ser viewed_policy
