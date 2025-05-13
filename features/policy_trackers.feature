Feature: Policy trackers
  As a player
  I want the policy trackers to be correctly implemented
  So that game progress can be tracked and powers unlocked appropriately

  Scenario: Liberal policy tracker setup
    Given the game has begun
    And roles haven't been assigned
    When the game is initialized
    Then the liberal policy tracker should have 5 slots

  Scenario: Liberal policy tracker extended setup
    Given the game has begun
    And roles haven't been assigned
    And the liberal tracker is set to extended mode
    When the game is initialized
    Then the liberal policy tracker should have 6 slots

  Scenario: Fascist policy tracker setup with less than 8 players
    Given the game has 7 players
    And roles haven't been assigned
    When the game is initialized
    Then the fascist policy tracker should have 6 slots
    And the 3rd slot should have the Policy Peek power
    And the 4th slot should have the Execution power
    And the 5th slot should have the Execution power
    And the 6th slot should not have a power

  Scenario: Fascist policy tracker setup with 9-10 players
    Given the game has 10 players
    When the game is initialized
    Then the fascist policy tracker should have 6 slots
    And the 2nd slot should have the Investigate Loyalty power
    And the 3rd slot should have the Special Election power
    And the 4th slot should have the Execution power
    And the 5th slot should have the Execution power
    And the 6th slot should not have a power

  Scenario: Fascist policy tracker setup with 11+ players
    Given the game has 11 players
    When the game is initialized
    Then the fascist policy tracker should have 6 slots
    And the 1st slot should have the Investigate Loyalty power
    And the 2nd slot should have the Investigate Loyalty power
    And the 3rd slot should have the Special Election power
    And the 4th slot should have the Execution power
    And the 5th slot should have the Execution power
    And the 6th slot should not have a power

  Scenario: Communist policy tracker setup with less than 8 players
    Given the game has 7 players
    And communists are in play
    When the game is initialized
    Then the communist policy tracker should have 5 slots
    And the 1st slot should have the Bugging power
    And the 2nd slot should have the Radicalization power
    And the 3rd slot should have the Five-Year Plan power
    And the 4th slot should have the Congress power
    And the 5th slot should not have a power

  Scenario: Communist policy tracker setup with 9-10 players
    Given the game has 10 players
    And communists are in play
    When the game is initialized
    Then the communist policy tracker should have 6 slots
    And the 1st slot should have the Bugging power
    And the 2nd slot should have the Radicalization power
    And the 3rd slot should have the Five-Year Plan power
    And the 4th slot should have the Congress power
    And the 5th slot should have the Confession power
    And the 6th slot should not have a power

  Scenario: Communist policy tracker setup with 11+ players
    Given the game has 11 players
    And communists are in play
    When the game is initialized
    Then the communist policy tracker should have 6 slots
    And the 1st slot should not have a power
    And the 2nd slot should have the Radicalization power
    And the 3rd slot should have the Five-Year Plan power
    And the 4th slot should have the Radicalization power
    And the 5th slot should have the Confession power
    And the 6th slot should not have a power
