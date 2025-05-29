Feature: Funcionalidad de la estrategia base

  Como sistema de estrategias de jugador,
  quiero definir una interfaz abstracta común para todas las estrategias,
  para asegurar que todas las implementaciones tengan los métodos necesarios para el juego.
  Scenario: Inicialización de estrategia base
    Given una estrategia base con un jugador mock
    Then la estrategia debe tener una referencia al jugador
    And la estrategia debe ser una instancia de PlayerStrategy

  Scenario: Verificación de métodos abstractos de fase electoral
    Given la clase PlayerStrategy
    Then PlayerStrategy debe definir método abstracto "nominate_chancellor"
    And PlayerStrategy debe definir método abstracto "vote"

  Scenario: Verificación de métodos abstractos de fase legislativa
    Given la clase PlayerStrategy
    Then PlayerStrategy debe definir método abstracto "filter_policies"
    And PlayerStrategy debe definir método abstracto "choose_policy"
    And PlayerStrategy debe definir método abstracto "veto"
    And PlayerStrategy debe definir método abstracto "accept_veto"

  Scenario: Verificación de métodos abstractos de poderes ejecutivos
    Given la clase PlayerStrategy
    Then PlayerStrategy debe definir método abstracto "choose_player_to_kill"
    And PlayerStrategy debe definir método abstracto "choose_player_to_inspect"
    And PlayerStrategy debe definir método abstracto "choose_next_president"
    And PlayerStrategy debe definir método abstracto "choose_player_to_mark"

  Scenario: Verificación de métodos abstractos de poderes comunistas
    Given la clase PlayerStrategy
    Then PlayerStrategy debe definir método abstracto "choose_player_to_radicalize"
    And PlayerStrategy debe definir método abstracto "choose_player_to_bug"

  Scenario: Verificación de métodos abstractos de poderes especiales
    Given la clase PlayerStrategy
    Then PlayerStrategy debe definir método abstracto "propaganda_decision"
    And PlayerStrategy debe definir método abstracto "choose_revealer"
    And PlayerStrategy debe definir método abstracto "pardon_player"

  Scenario: Verificación de métodos abstractos de mecánicas avanzadas
    Given la clase PlayerStrategy
    Then PlayerStrategy debe definir método abstracto "chancellor_veto_proposal"
    And PlayerStrategy debe definir método abstracto "vote_of_no_confidence"
    And PlayerStrategy debe definir método abstracto "social_democratic_removal_choice"

  Scenario: Estrategia base no puede ser instanciada directamente
    Given la clase PlayerStrategy
    When intento crear una instancia directa de PlayerStrategy
    Then debe lanzar una excepción TypeError

  Scenario: Implementación concreta debe implementar todos los métodos
    Given una implementación incompleta de PlayerStrategy
    When intento crear una instancia de la implementación incompleta
    Then debe lanzar una excepción TypeError
  Scenario: Verificación de interfaz completa
    Given la clase PlayerStrategy
    Then debe tener exactamente 18 métodos abstractos
    And todos los métodos deben estar marcados como abstractos
