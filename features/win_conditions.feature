Feature: Win conditions
  As a player
  I want the game to correctly identify when a team has won
  So that games can conclude properly

  Scenario: Liberal win by policy count
    Given the game is in progress
    When 5 liberal policies are enacted
    Then the game should end
    And liberals should win

  Scenario: Liberal win by assassinating Hitler
    Given the game is in progress
    And the President has the Execution power
    And the target player is Hitler
    When the President executes Hitler
    Then the game should end
    And liberals should win

  Scenario: Fascist win by policy count
    Given the game is in progress
    When 6 fascist policies are enacted
    Then the game should end
    And fascists should win

  Scenario: Fascist win by electing Hitler
    Given the game is in progress
    And 3 or more fascist policies have been enacted
    And Hitler is the chancellor candidate
    When the vote results in a majority of Ja
    Then the game should end
    And fascists should win

  Scenario: Communist win by policy count
    Given the game is in progress
    And communists are in play
    When the communist policy tracker is filled
    Then the game should end
    And communists should win

  Scenario: Communist win by assassinating Hitler
    Given the game is in progress
    And communists are in play
    And the President has the Execution power
    And the target player is Hitler
    When the President executes Hitler
    Then the game should end
    And both liberals and communists should win
