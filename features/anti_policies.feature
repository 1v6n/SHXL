Feature: Anti-policies mechanics
  As a game host
  I want to include anti-policies to balance the game
  So that it can be extended and more balanced

  Scenario: Anti-Communist policy effects
    Given the game is in progress
    And anti-policies are in play
    And there is at least one communist policy on the tracker
    When an anti-communist policy is enacted
    Then it should be placed on the fascist tracker
    And the President should remove a communist policy from the communist tracker
    And the next communist policy enacted should not grant a presidential power

  Scenario: Anti-Fascist policy effects
    Given the game is in progress
    And anti-policies are in play
    And there is at least one fascist policy on the tracker
    When an anti-fascist policy is enacted
    Then it should be placed on the communist tracker
    And the President should remove a fascist policy from the fascist tracker
    And the next fascist policy enacted should not grant a presidential power

  Scenario: Social Democratic policy effects
    Given the game is in progress
    And anti-policies are in play
    And liberals are significantly disadvantaged
    When a social democratic policy is enacted
    Then it should be placed on the liberal tracker
    And the President should remove either a fascist or communist policy
    And neither the fascists nor communists should reuse presidential powers for the removed policy
