Feature: Legislative phase mechanics
  As a player
  I want the game to correctly implement the legislative phase
  So that policies are properly enacted

  Scenario: President draws and discards policies
    Given it is the legislative phase
    And player 1 is the President
    And player 2 is the Chancellor
    When the legislative session begins
    Then the President should draw 3 policy tiles
    And the President should discard 1 policy face-down to the discard pile
    And the President should pass 2 policies to the Chancellor

  Scenario: Chancellor enacts a policy
    Given it is the legislative phase
    And the President has passed 2 policies to the Chancellor
    When the Chancellor receives the policies
    Then the Chancellor should discard 1 policy face-down to the discard pile
    And the Chancellor should enact the remaining policy
    And the enacted policy should be placed face-up on the corresponding tracker

  Scenario: No communication during policy selection
    Given it is the legislative phase
    And the President has drawn 3 policies
    When the President is selecting which policy to discard
    Then no communication between players should be allowed
    
  Scenario: Policy deck replenishment
    Given it is the legislative phase
    And there are less than 3 policy tiles remaining in the policy deck
    When the legislative session ends
    Then the discard pile should be added and shuffled to the policy deck

  Scenario: Executive action after fascist policy
    Given it is the legislative phase
    And a fascist policy is enacted
    And that policy grants a presidential power
    Then the legislative phase should end
    And the executive action phase should begin
    And the President should use the granted power

  Scenario: Executive action after communist policy
    Given it is the legislative phase
    And a communist policy is enacted
    And that policy grants a presidential power
    Then the legislative phase should end
    And the executive action phase should begin
    And the President should use the granted power

  Scenario: New round after liberal policy
    Given it is the legislative phase
    And a liberal policy is enacted
    Then the legislative phase should end
    And a new round should begin with a new election

  Scenario: Veto power availability
    Given 5 fascist policies have been enacted
    When the legislative phase begins
    Then the veto power should be available

  Scenario: Chancellor proposes veto
    Given it is the legislative phase
    And the veto power is available
    And the President has passed 2 policies to the Chancellor
    When the Chancellor proposes a veto
    Then the President should be able to accept or reject the veto

  Scenario: Successful veto
    Given it is the legislative phase
    And the Chancellor has proposed a veto
    When the President accepts the veto
    Then both policies should be discarded
    And the President placard should pass to the left
    And the Election Tracker should advance by one

  Scenario: Rejected veto
    Given it is the legislative phase
    And the Chancellor has proposed a veto
    When the President rejects the veto
    Then the Chancellor must enact one of the policies
