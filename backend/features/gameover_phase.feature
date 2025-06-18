Feature: Gestión de la fase de fin de juego

  Como sistema de juego
  quiero manejar correctamente la fase de fin de juego,
  para garantizar que el juego termine apropiadamente y revele toda la información necesaria.

  Background:
    Given a new SHXLGame instance

  Scenario: GameOverPhase ejecuta y marca el juego como terminado
    Given un objeto GameOverPhase con el juego
    When ejecuto la fase de game over
    Then el estado del juego debe marcarse como terminado
    And debe retornar la misma instancia de GameOverPhase
    And todos los roles deben estar revelados
  Scenario: GameOverPhase inicializa correctamente
    Given un objeto SHXLGame configurado para gameover
    When creo una nueva GameOverPhase
    Then la fase gameover debe tener una referencia al juego
    And debe implementar el método execute de gameover

  Scenario: GameOverPhase mantiene el estado terminal
    Given un objeto GameOverPhase configurado
    And el juego ya está marcado como terminado
    When ejecuto la fase de game over múltiples veces
    Then siempre debe retornar la misma instancia
    And el estado del juego debe permanecer terminado
