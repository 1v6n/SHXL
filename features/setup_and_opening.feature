Feature: Game setup and opening phase
  As a game host
  I want to properly set up the game and conduct the opening phase
  So that players can start with the correct information

  Scenario: Create and distribute envelopes
    Given the game is starting
    When the envelopes are prepared
    Then each player should receive an envelope
    And each envelope should contain a secret role card and a party membership card
    And each envelope should have Ja and Nein ballot cards

  Scenario: Select first presidential candidate
    Given the game has started
    And the roles have been assigned
    And each party knows their members if applicable
    When the game is in the opening phase
    Then a random player should be selected as the first presidential candidate
    And that player should receive the President and Chancellor placards

  Scenario: Fascists knowledge of Hitler with less than 8 players
    Given the game has started
    And the game has less than 8 players
    And the roles have been assigned
    When the opening phase begins
    Then fascists should know each other
    And Hitler should know the fascists
    And liberals should not know anyone's roles

  Scenario: Fascists knowledge of Hitler with 8 or more players
    Given the game has started
    And the game has more than 7 players
    And the roles have been assigned
    When the opening phase begins
    Then fascists should know each other
    And fascists should know who Hitler is
    And Hitler should not know who the fascists are
    And liberals should not know anyone's roles

  Scenario: Communists knowledge with less than 11 players
    Given the game has started
    And the game has less than 11 players
    And communists are in play
    And the roles have been assigned
    When the opening phase begins
    Then communists should know each other
    And communists should not know fascists or Hitler
    And fascists should not know communists

  Scenario: Communists knowledge with 11 or more players
    Given the game has started
    And the game has more than 10 players
    And communists are in play
    And the roles have been assigned
    When the opening phase begins
    Then communists should not know each other
    And communists should not know fascists or Hitler
    And fascists should not know communists
