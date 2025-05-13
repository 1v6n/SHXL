Feature: Executive action phase mechanics
  As a player
  I want the game to correctly implement executive actions
  So that presidential powers function as intended

  # Fascist Powers
  
  Scenario: Investigate Loyalty power
    Given it is the executive action phase
    And the President has the Investigate Loyalty power
    When the President chooses to investigate player 3
    Then the President should see player 3's party membership card
    And the President should return the card to player 3
    And player 3 should not be eligible for investigation again in this game

  Scenario: Call Special Election power
    Given it is the executive action phase
    And the President has the Call Special Election power
    When the President chooses player 3 for the special election
    Then player 3 should become the next Presidential Candidate
    And the special election should be held
    And after the special election the presidency should return to the player left of the current President

  Scenario: Policy Peek power
    Given it is the executive action phase
    And the President has the Policy Peek power
    When the President uses the power
    Then the President should see the top 3 policy tiles
    And the policy tiles should remain in the same order

  Scenario: Execution power
    Given it is the executive action phase
    And the President has the Execution power
    When the President chooses to execute player 3
    Then player 3 should be eliminated from the game
    And player 3 should not be able to vote, speak, or run for office

  Scenario: Liberals win if Hitler is executed
    Given it is the executive action phase
    And the President has the Execution power
    And player 3 is Hitler
    When the President chooses to execute player 3
    Then the game should end
    And liberals should win

  # Communist Powers
  
  Scenario: Confession power
    Given it is the executive action phase
    And the President has the Confession power
    When the President uses the power
    Then the President's party membership should be revealed to all players

  Scenario: Bugging power
    Given it is the executive action phase
    And the President has the Bugging power
    When the President chooses player 3 to bug
    Then communists should see player 3's party membership card

  Scenario: Five-Year Plan power
    Given it is the executive action phase
    And the President has the Five-Year Plan power
    When the President uses the power
    Then 2 communist policies and 1 liberal policy should be added to the draw deck

  Scenario: Congress power
    Given it is the executive action phase
    And the President has the Congress power
    When the President uses the power
    Then communists should learn who the original communists are

  Scenario: Radicalization power
    Given it is the executive action phase
    And the President has the Radicalization power
    When the President chooses player 3 to radicalize
    Then player 3's party membership should be swapped with a communist party card
    
  Scenario: Radicalization cannot convert Hitler
    Given it is the executive action phase
    And the President has the Radicalization power
    And player 3 is Hitler
    When the President chooses player 3 to radicalize
    Then player 3 should remain Hitler and fascist
