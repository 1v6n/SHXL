Feature: Ejecución unitaria de poderes especiales en SHXLGame
  Como desarrollador,
  quiero verificar cada poder (InvestigateLoyalty, SpecialElection, PolicyPeek, etc.)
  usando mocks mínimos,
  para asegurar que cada clase Power modifica o devuelve exactamente lo que debe.

  Scenario: InvestigateLoyalty retorna la afiliación y marca investigado
    Given un "game" mock con estado vacío para investigar
    And un jugador objetivo con party_membership "communist"
    When ejecuto InvestigateLoyalty sobre ese jugador
    Then el resultado debe ser "communist"
    And el estado investigado debe contener al mismo jugador

  Scenario: SpecialElection asigna un próximo presidente temporal
    Given un "game" mock con un presidente actual que tiene id 42
    And la lista special_election_return_index es None
    When ejecuto SpecialElection nominando al jugador mock con id 17
    Then game.state.special_election debe ser true
    And game.state.president_candidate debe ser ese jugador con id 17
    And game.state.special_election_return_index debe quedar en 42

  Scenario: PolicyPeek devuelve las tres primeras políticas sin modificar el mazo
    Given un "game" mock con board policies "L1,L2,L3,X,Y"
    When ejecuto PolicyPeek
    Then el resultado PolicyPeek debe ser "L1,L2,L3"
    And la pila original debe seguir siendo de tamaño 5

  Scenario: Execution marca un jugador como muerto y lo quita de active_players
    Given un "game" mock con active_players con ids "0,1,2"
    And el jugador con id 2 está vivo inicialmente
    When ejecuto Execution sobre el jugador con id 2
    Then el jugador con id 2 debe estar muerto
    And el jugador con id 2 no debe estar en active_players

  Scenario: Confession revela la afiliación del presidente actual
    Given un "game" mock cuyo president tiene id 5 y party_membership "fascist"
    When ejecuto Confession
    Then el resultado debe ser "fascist"
    And game.state.revealed_affiliations con id 5 debe ser "fascist"

  Scenario: Bugging permite a todos los comunistas conocer afiliación de un objetivo
    Given un "game" mock con jugadores comunistas ids "2,3" y objetivo id 7 con party "liberal"
    When ejecuto Bugging sobre el jugador objetivo
    Then cada jugador comunista debe conocer la afiliación del objetivo como "liberal"

  Scenario: FiveYearPlan agrega 2 communists y 1 liberal al tope del mazo
    Given un "game" mock con board policies "A,B,C"
    When ejecuto FiveYearPlan
    Then el mazo debe tener 6 cartas en total
    And las primeras tres cartas deben ser communist, communist, liberal

  Scenario: Congress comparte la lista de id de comunistas originales
    Given un "game" mock con jugadores de partidos:
      | id | party     |
      | 0  | communist |
      | 1  | liberal   |
      | 2  | communist |
      | 3  | fascist   |
    When ejecuto Congress
    Then el resultado Congress debe contener ids "0,2"
    And cada jugador comunista debe conocer a los comunistas "0,2"

  Scenario: Radicalization convierte a un jugador a comunista salvo si es Hitler
    Given un "game" mock con un jugador target id 8 que no es Hitler
    And el target tiene party_membership "liberal"
    When ejecuto Radicalization sobre ese jugador
    Then el resultado no debe ser None
    And el target debe tener party_membership "communist"

  Scenario: Radicalization NO convierte a Hitler
    Given un "game" mock con un jugador target id 9 que es Hitler
    And el target tiene party_membership "fascist"
    When ejecuto Radicalization sobre ese jugador
    Then el resultado debe ser None
    And el target debe seguir con party_membership "fascist"

  Scenario: Propaganda permite al presidente ver y descartar la primera carta
    Given un "game" mock con board policies "X,Y,Z"
    And el presidente siempre decide descartar en propaganda
    When ejecuto Propaganda
    Then el resultado debe ser "X"
    And la primera carta del mazo debe ser "Y"

  Scenario: Impeachment hace que el canciller revele la afiliación del objetivo
    Given un "game" mock con jugador target id 6 party "communist" y revealer id 2
    When ejecuto Impeachment del target al revealer
    Then el método debe devolver True
    And el revealer debe conocer la afiliación del target como "communist"
