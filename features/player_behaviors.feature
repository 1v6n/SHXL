Feature: Player behaviors and abilities
  As a player
  I want various player roles and interfaces implemented correctly
  So that I can make decisions according to my role

  Scenario: Player nomination of chancellor
    Given it is the election phase
    And player 1 is the President
    When player 1 is prompted to nominate a chancellor
    Then player 1 should be able to select any eligible player
    And ineligible players should not be selectable

  Scenario: Player filtering of policies as president
    Given it is the legislative phase
    And player 1 is the President
    When player 1 receives 3 policy tiles
    Then player 1 should be able to discard 1 policy
    And pass the remaining 2 policies to the Chancellor

  Scenario: Player enactment of policy as chancellor
    Given it is the legislative phase
    And player 2 is the Chancellor
    When player 2 receives 2 policy tiles from the President
    Then player 2 should be able to discard 1 policy
    And enact the remaining policy

  Scenario: Player voting on proposed government
    Given it is the election phase
    And a government has been proposed
    When players are prompted to vote
    Then each player should be able to vote Ja or Nein

  Scenario: Player using veto power as chancellor
    Given it is the legislative phase
    And 5 fascist policies have been enacted
    And player 2 is the Chancellor
    When player 2 receives 2 policies
    Then player 2 should be able to propose a veto

  Scenario: Player viewing policies with Policy Peek
    Given it is the executive action phase
    And the President has the Policy Peek power
    When the President uses the power
    Then the President should see the top 3 policy tiles
    And other players should not see these tiles

  Scenario: Player executing another player
    Given it is the executive action phase
    And the President has the Execution power
    When the President is prompted to choose a player to execute
    Then the President should be able to select any living player
    And the executed player should be eliminated from the game

  Scenario: Player inspecting another player's loyalty
    Given it is the executive action phase
    And the President has the Investigate Loyalty power
    When the President is prompted to choose a player to investigate
    Then the President should be able to select any uninvestigated living player
    And the President should see that player's party membership card
    And other players should not see this information

  Scenario: Player choosing next president for special election
    Given it is the executive action phase
    And the President has the Special Election power
    When the President is prompted to choose the next president
    Then the President should be able to select any living player
    And that player should become the next Presidential Candidate

  Scenario: Player abilities after being executed
    Given player 3 has been executed
    When a vote is required
    Then player 3 should not be able to vote
    And player 3 should not be eligible for nomination as Chancellor
    And player 3 should not be eligible to become President
