Feature: Election phase mechanics
  As a player
  I want the game to correctly implement the election phase
  So that governments are properly formed

  Scenario: President rotation after the first round
    Given the game has started
    And one round has completed
    When the next round begins
    Then the President placard should move clockwise to the next player

  Scenario: Chancellor nomination
    Given it is the election phase
    And player 1 is the current presidential candidate
    When player 1 nominates player 2 as chancellor
    Then player 3 should become the chancellor candidate
    And the Chancellor placard should be passed to player 3

  Scenario: Term limits for Chancellor nomination
    Given it is the election phase
    And player 1 was the last elected President
    And player 2 was the last elected Chancellor
    And player 3 is the current presidential candidate
    When player 3 nominates a chancellor
    Then player 1 should not be eligible to be nominated
    But player 2 should not be eligible to be nominated

  Scenario: Term limits with 5 players remaining
    Given the game has started
    And 5 players remain in the game
    And player 1 was the last elected President
    And player 2 was the last elected Chancellor
    And player 3 is the current presidential candidate
    When player 3 nominates a chancellor
    Then player 1 should be eligible to be nominated
    But player 2 should not be eligible to be nominated

  Scenario: Vote for government
    Given it is the election phase
    And player 1 is the presidential candidate
    And player 2 is the chancellor candidate
    When all players vote
    And the vote results in a majority of Ja
    Then the government should be elected
    And player 1 should become President
    And player 2 should become Chancellor

  Scenario: Fascist win if Hitler is elected Chancellor after 3 fascist policies
    Given it is the election phase
    And 3 fascist policies have been enacted
    And player 1 is the presidential candidate
    And player 2 is the chancellor candidate
    And player 2 is Hitler
    When all players vote
    And the vote results in a majority of Ja
    Then the game should end
    And fascists should win

  Scenario: Failed vote for government
    Given it is the election phase
    And player 1 is the presidential candidate
    And player 2 is the chancellor candidate
    When all players vote
    And the vote results in a majority of Nein
    Then the government should not be elected
    And the President placard should move clockwise to the next player
    And the Election Tracker should advance by one

  Scenario: Election Tracker causing chaos
    Given it is the election phase
    And the Election Tracker is at 2
    When the vote results in a majority of Nein
    Then the Election Tracker should reach 3
    And the top policy from the policy deck should be automatically enacted
    And any presidential power from that policy should be ignored
    And the Election Tracker should reset to 0
    And all players should become eligible to be Chancellor in the next election

  Scenario Outline: Policy enactment resets Election Tracker
    Given the Election Tracker is at <initial_value>
    When a policy is enacted
    Then the Election Tracker should reset to 0

  Examples:
    | initial_value |
    | 1             |
    | 2             |
