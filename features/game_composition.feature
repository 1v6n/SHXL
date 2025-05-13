Feature: Game composition based on player count
  As a game host
  I want the game to have the correct number of roles and policies based on player count
  So that the game is properly balanced

  Scenario Outline: Parties are asigned based on number of players and communist participation
    Given the game has <players> players
    And communists are <communists_in_play>
    When parties are asigned
    Then there should be <liberals> liberals, <fascists> fascists (including Hitler), and <communists> communists

    Examples:
      | players | communists_in_play | liberals | fascists | communists |
      | 6       | false              | 4        | 2        | 0          |
      | 7       | false              | 4        | 3        | 0          |
      | 8       | false              | 5        | 3        | 0          |
      | 9       | false              | 5        | 4        | 0          |
      | 10      | false              | 6        | 4        | 0          |
      | 11      | false              | 6        | 5        | 0          |
      | 12      | false              | 7        | 5        | 0          |
      | 13      | false              | 7        | 6        | 0          |
      | 14      | false              | 8        | 6        | 0          |
      | 15      | false              | 8        | 7        | 0          |
      | 16      | false              | 9        | 7        | 0          |
      | 6       | true               | 3        | 2        | 1          |
      | 7       | true               | 4        | 2        | 1          |
      | 8       | true               | 4        | 3        | 1          |
      | 9       | true               | 4        | 3        | 2          |
      | 10      | true               | 5        | 3        | 2          |
      | 11      | true               | 5        | 4        | 2          |
      | 12      | true               | 6        | 4        | 2          |
      | 13      | true               | 6        | 4        | 3          |
      | 14      | true               | 7        | 4        | 3          |
      | 15      | true               | 7        | 5        | 3          |
      | 16      | true               | 7        | 5        | 4          |

  Scenario Outline: Standard policy distribution by player count
    Given the game has <players> players
    And communists are <communists_in_play>
    When the policy deck is created
    Then the deck should contain <communist> communist policies, <liberal> liberal policies, and <fascist> fascist policies

    Examples:
      | players | communists_in_play | liberal | fascist | communist |
      | 5       | false              | 6       | 11      | 0         |
      | 6       | false              | 6       | 11      | 0         |
      | 7       | false              | 6       | 11      | 0         |
      | 8       | false              | 6       | 11      | 0         |
      | 9       | false              | 6       | 11      | 0         |
      | 10      | false              | 6       | 11      | 0         |
      | 11      | false              | 6       | 11      | 0         |
      | 12      | false              | 6       | 11      | 0         |
      | 13      | false              | 6       | 11      | 0         |
      | 14      | false              | 6       | 11      | 0         |
      | 15      | false              | 6       | 11      | 0         |
      | 16      | false              | 6       | 11      | 0         |
      | 6       | true               | 5       | 10      | 8         |
      | 7       | true               | 5       | 10      | 8         |
      | 8       | true               | 6       | 9       | 8         |
      | 9       | true               | 6       | 9       | 8         |
      | 10      | true               | 6       | 9       | 8         |
      | 11      | true               | 6       | 9       | 8         |
      | 12      | true               | 6       | 9       | 8         |
      | 13      | true               | 6       | 9       | 8         |
      | 14      | true               | 6       | 9       | 8         |
      | 15      | true               | 6       | 9       | 8         |
      | 16      | true               | 6       | 9       | 8         |

  Scenario Outline: Emergency powers cards are included for large games
    Given the game has <players> players
    And communists are <communists_in_play>
    When the policy deck is created
    Then <emergency_cards> emergency cards should be added
    And there should be <article_48> Article 48 cards and <enabling_acts> Enabling Act cards

    Examples:
      | players | communists_in_play | emergency_cards | article_48 | enabling_acts |
      | 10      | false              | 0               | 0          | 0             |
      | 11      | false              | 1               | 1          | 0             |
      | 12      | false              | 2               | 1          | 1             |
      | 13      | false              | 3               | 2          | 1             |
      | 14      | false              | 4               | 2          | 2             |
      | 15      | false              | 5               | 3          | 2             |
      | 16      | false              | 6               | 3          | 3             |
      | 10      | true               | 0               | 0          | 0             |
      | 11      | true               | 0               | 0          | 0             |
      | 12      | true               | 0               | 0          | 0             |
      | 13      | true               | 0               | 0          | 0             |
      | 14      | true               | 2               | 1          | 1             |
      | 15      | true               | 4               | 2          | 2             |
      | 15      | true               | 6               | 3          | 3             |