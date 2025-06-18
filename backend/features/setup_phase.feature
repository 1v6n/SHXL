Feature: Gestión de la fase de configuración del juego

  Como sistema de juego
  quiero manejar correctamente la fase de configuración inicial,
  para garantizar que el juego se configure adecuadamente antes de comenzar.

  Background:
    Given a new SHXLGame instance
  Scenario: SetupPhase ejecuta y retorna ElectionPhase
    Given un objeto SetupPhase con el juego
    When ejecuto la fase de configuración
    Then debe retornar una instancia de ElectionPhase
    And el resultado debe ser una ElectionPhase con referencia al juego
  Scenario: SetupPhase inicializa correctamente
    Given un objeto SHXLGame configurado para setup
    When creo una nueva SetupPhase
    Then la fase setup debe tener una referencia al juego
    And debe implementar el método execute de setup
