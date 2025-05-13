Feature: Emergency powers mechanics
  As a game host
  I want to include emergency powers for large games
  So that non-fascist players have better chances to identify and eliminate Hitler

  # Article 48 (President Powers)
  
  Scenario: Article 48 - Propaganda power
    Given the game is in progress
    And emergency powers are in play
    And the President has an Article 48 card
    When the President uses the Propaganda power
    Then the President should view the top card of the policy deck
    And the President should choose to discard it or put it back
    And the Article 48 card should be removed from the game

  Scenario: Article 48 - Policy Peek power
    Given the game is in progress
    And emergency powers are in play
    And the President has an Article 48 card
    When the President uses the Policy Peek power
    Then the President should view the top 3 cards of the policy deck
    And the cards should not be reordered
    And the Article 48 card should be removed from the game

  Scenario: Article 48 - Impeachment power
    Given the game is in progress
    And emergency powers are in play
    And the President has an Article 48 card
    When the President uses the Impeachment power on player 3
    Then the Chancellor should reveal their party to player 3
    And the Article 48 card should be removed from the game

  Scenario: Article 48 - Marked for Execution power
    Given the game is in progress
    And emergency powers are in play
    And the President has an Article 48 card
    When the President marks player 3 for execution
    Then player 3 should be executed after 3 fascist policies are enacted
    And the Article 48 card should be removed from the game

  Scenario: Article 48 - Execution power
    Given the game is in progress
    And emergency powers are in play
    And the President has an Article 48 card
    When the President executes player 3
    Then player 3 should be eliminated from the game
    And player 3's role should not be revealed unless they are Hitler
    And the Article 48 card should be removed from the game

  Scenario: Article 48 - Pardon power
    Given the game is in progress
    And emergency powers are in play
    And the President has an Article 48 card
    And player 3 has been marked for execution
    When the President pardons player 3
    Then player 3 should no longer be marked for execution
    And the Article 48 card should be removed from the game

  # Enabling Act (Chancellor Powers)
  
  Scenario: Enabling Act - Propaganda power
    Given the game is in progress
    And emergency powers are in play
    And the Chancellor has an Enabling Act card
    When the Chancellor uses the Propaganda power
    Then the Chancellor should view the top card of the policy deck
    And the Chancellor should choose to discard it or put it back
    And the Enabling Act card should be removed from the game

  Scenario: Enabling Act - Policy Peek power
    Given the game is in progress
    And emergency powers are in play
    And the Chancellor has an Enabling Act card
    When the Chancellor uses the Policy Peek power
    Then the Chancellor should view the top 3 cards of the policy deck
    And the cards should not be reordered
    And the Enabling Act card should be removed from the game

  Scenario: Enabling Act - Impeachment power
    Given the game is in progress
    And emergency powers are in play
    And the Chancellor has an Enabling Act card
    When the Chancellor uses the Impeachment power on player 3
    Then the President should reveal their party to player 3
    And the Enabling Act card should be removed from the game

  Scenario: Enabling Act - Marked for Execution power
    Given the game is in progress
    And emergency powers are in play
    And the Chancellor has an Enabling Act card
    When the Chancellor marks player 3 for execution
    Then player 3 should be executed after 3 fascist policies are enacted
    And the Enabling Act card should be removed from the game

  Scenario: Enabling Act - Execution power
    Given the game is in progress
    And emergency powers are in play
    And the Chancellor has an Enabling Act card
    When the Chancellor executes player 3
    Then player 3 should be eliminated from the game
    And player 3's role should not be revealed unless they are Hitler
    And the Enabling Act card should be removed from the game

  Scenario: Enabling Act - Vote of No Confidence power
    Given the game is in progress
    And emergency powers are in play
    And the Chancellor has an Enabling Act card
    And a policy has been discarded in the current legislative phase
    When the Chancellor uses the Vote of No Confidence power
    Then the discarded policy by the President should be enacted
    And the Enabling Act card should be removed from the game
