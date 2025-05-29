Feature: Funcionalidad del jugador humano

  Como jugador humano,
  quiero interactuar con el juego a través de la consola,
  para tomar decisiones durante las diferentes fases del juego.

  Scenario: Inicialización de jugador humano
    Given un jugador humano con ID 1, nombre "Human Player", role "liberal", y estado de juego
    Then el jugador humano debe tener ID 1
    And el jugador humano debe tener nombre "Human Player"
    And el jugador humano debe tener role "liberal"
    And el jugador humano debe heredar propiedades de Player abstracto

  Scenario: Nominación de canciller con jugadores elegibles
    Given un jugador humano como presidente
    And hay 3 jugadores elegibles para canciller
    When el jugador humano nomina un canciller con input "1"
    Then debe retornar el jugador con ID 1
    And debe mostrar información del role

  Scenario: Filtrar políticas como presidente
    Given un jugador humano como presidente
    And 3 políticas disponibles: "liberal", "fascist", "communist"
    When el jugador humano filtra políticas con input "2"
    Then debe retornar 2 políticas elegidas y 1 descartada
    And la política en posición 2 debe ser descartada

  Scenario: Elegir política como canciller
    Given un jugador humano como canciller
    And 2 políticas disponibles: "liberal", "fascist"
    When el jugador humano elige política con input "1"
    Then debe retornar la política en posición 1 y descartar la otra

  Scenario: Votación en gobierno con voto positivo
    Given un jugador humano en votación
    When el jugador humano vota con input "yes"
    Then debe retornar True

  Scenario: Votación en gobierno con voto negativo
    Given un jugador humano en votación
    When el jugador humano vota con input "no"
    Then debe retornar False

  Scenario: Decisión de veto como canciller
    Given un jugador humano como canciller
    And políticas disponibles para veto
    When el jugador humano decide veto con input "yes"
    Then debe retornar True

  Scenario: Aceptar veto como presidente
    Given un jugador humano como presidente
    And el canciller propuso veto
    When el jugador humano acepta veto con input "yes"
    Then debe retornar True

  Scenario: Rechazar veto como presidente
    Given un jugador humano como presidente
    And el canciller propuso veto
    When el jugador humano acepta veto con input "no"
    Then debe retornar False

  Scenario: Ver políticas con Policy Peek
    Given un jugador humano con poder de Policy Peek
    And 3 políticas en el top del deck: "liberal", "fascist", "communist"
    When el jugador humano ve las políticas
    Then debe mostrar las 3 políticas
    And debe esperar confirmación del jugador

  Scenario: Ejecutar jugador inmediatamente
    Given un jugador humano con poder de ejecución
    And 4 jugadores disponibles para ejecutar
    When el jugador humano ejecuta con input "2"
    Then debe retornar el jugador con ID 2

  Scenario: Marcar jugador para ejecución
    Given un jugador humano con poder de marcado
    And 4 jugadores disponibles para marcar
    When el jugador humano marca con input "3"
    Then debe retornar el jugador con ID 3

  Scenario: Inspeccionar jugador no inspeccionado antes
    Given un jugador humano con poder de inspección
    And 3 jugadores no inspeccionados disponibles
    When el jugador humano inspecciona con input "2"
    Then debe retornar el jugador con ID 2

  Scenario: Inspeccionar jugador cuando todos fueron inspeccionados
    Given un jugador humano con poder de inspección
    And todos los jugadores fueron inspeccionados previamente
    When el jugador humano inspecciona con input "1"
    Then debe permitir inspeccionar cualquier jugador
    And debe retornar el jugador con ID 1

  Scenario: Elegir siguiente presidente en elección especial
    Given un jugador humano con poder de elección especial
    And 4 jugadores elegibles como presidente
    When el jugador humano elige siguiente presidente con input "3"
    Then debe retornar el jugador con ID 3

  Scenario: Radicalizar jugador a comunista
    Given un jugador humano comunista con poder de radicalización
    And 3 jugadores disponibles para radicalizar
    When el jugador humano radicaliza con input "2"
    Then debe retornar el jugador con ID 2

  Scenario: Decisión de propaganda - descartar política
    Given un jugador humano con poder de propaganda
    And política top "fascist"
    When el jugador humano decide propaganda con input "yes"
    Then debe retornar True

  Scenario: Decisión de propaganda - mantener política
    Given un jugador humano con poder de propaganda
    And política top "liberal"
    When el jugador humano decide propaganda con input "no"
    Then debe retornar False

  Scenario: Elegir revelador para impeachment
    Given un jugador humano con poder de impeachment
    And 3 jugadores elegibles para revelar
    When el jugador humano elige revelador con input "1"
    Then debe retornar el jugador con ID 1

  Scenario: Remoción social demócrata - elegir fascist
    Given un jugador humano con poder social demócrata
    When el jugador humano elige remoción con input "fascist"
    Then debe retornar "fascist"

  Scenario: Remoción social demócrata - elegir communist
    Given un jugador humano con poder social demócrata
    When el jugador humano elige remoción con input "communist"
    Then debe retornar "communist"

  Scenario: Mostrar información de role para fascista
    Given un jugador humano fascista que conoce a hitler
    And conoce a otros fascistas
    When se muestra información del role
    Then debe mostrar información de hitler
    And debe mostrar lista de fascistas

  Scenario: Mostrar información de role para hitler en juego pequeño
    Given un jugador humano hitler en juego de 6 jugadores
    And conoce a otros fascistas
    When se muestra información del role
    Then debe mostrar lista de fascistas conocidos

  Scenario: Mostrar información de role para comunista
    Given un jugador humano comunista
    And conoce a otros comunistas
    When se muestra información del role
    Then debe mostrar lista de comunistas conocidos

  Scenario: Mostrar jugadores inspeccionados
    Given un jugador humano que inspeccionó previamente
    And el jugador 2 fue inspeccionado como "fascist"
    And el jugador 3 fue inspeccionado como "liberal"
    When se muestra información del role
    Then debe mostrar información de inspecciones previas

  Scenario: Manejo de input inválido en elección de jugador
    Given un jugador humano en proceso de elección
    And 3 jugadores disponibles con IDs 1, 2, 3
    When el jugador humano ingresa ID inválido "5"
    Then debe mostrar mensaje de error
    And debe solicitar nuevo input

  Scenario: Manejo de input no numérico
    Given un jugador humano en proceso de elección
    When el jugador humano ingresa texto "abc"
    Then debe mostrar mensaje de error numérico
    And debe solicitar nuevo input
