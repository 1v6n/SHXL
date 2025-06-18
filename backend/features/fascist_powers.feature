Feature: Poderes Fascistas
  Como jugador del juego Secret Hitler
  Quiero poder ejecutar poderes fascistas
  Para influir en el estado del juego según las reglas

  Background:
    Given que existe un juego fascista inicializado
    And que existe un jugador fascista con rol definido
    And que existe un jugador fascista objetivo con partido "Liberal"

  Scenario: Investigar la lealtad de un jugador fascista
    Given que tengo el poder fascista "InvestigateLoyalty"
    When ejecuto el poder fascista sobre el jugador objetivo
    Then el jugador debe ser marcado como investigado por fascistas
    And debo recibir la afiliación partidaria del jugador fascista objetivo

  Scenario: Investigar jugador con partido fascista
    Given que tengo el poder fascista "InvestigateLoyalty"
    And que el jugador fascista objetivo tiene partido "Fascist"
    When ejecuto el poder fascista sobre el jugador objetivo
    Then debo recibir "Fascist" como resultado fascista

  Scenario: Convocar elección especial fascista
    Given que tengo el poder fascista "SpecialElection"
    And que existe un candidato fascista para presidente especial
    When ejecuto el poder fascista de elección especial
    Then el estado fascista de elección especial debe activarse
    And el candidato fascista debe ser establecido como próximo presidente
    And el índice fascista de retorno debe guardarse correctamente

  Scenario: Espiar las próximas políticas fascistas
    Given que tengo el poder fascista "PolicyPeek"
    And que existen políticas fascistas en el mazo de al menos 3
    When ejecuto el poder fascista de espiar
    Then debo recibir las 3 políticas fascistas superiores del mazo
    And las políticas fascistas no deben ser removidas del mazo

  Scenario: Ejecutar a un jugador por poder fascista
    Given que tengo el poder fascista "Execution"
    And que el jugador fascista objetivo está vivo
    And que el jugador fascista objetivo está en lista de activos
    When ejecuto el poder fascista sobre el jugador objetivo
    Then el jugador fascista objetivo debe ser ejecutado
    And el jugador fascista debe ser removido de jugadores activos
    And debo recibir el jugador fascista ejecutado como resultado

  Scenario: Espiar políticas con mazo fascista insuficiente
    Given que tengo el poder fascista "PolicyPeek"
    And que existen solo 2 políticas fascistas en el mazo
    When ejecuto el poder fascista de espiar
    Then debo recibir solo las 2 políticas fascistas disponibles

  Scenario: Ejecutar jugador fascista ya muerto
    Given que tengo el poder fascista "Execution"
    And que el jugador fascista objetivo ya está muerto
    When ejecuto el poder fascista sobre el jugador objetivo
    Then el jugador fascista objetivo debe permanecer muerto
    And el resultado fascista debe ser el jugador objetivo
