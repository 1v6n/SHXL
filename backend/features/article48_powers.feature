Feature: Poderes del Artículo 48 del Presidente
  Como presidente en el juego
  Quiero usar los poderes especiales del Artículo 48
  Para influir en el desarrollo de la partida

  Scenario: El presidente usa propaganda para ver y descartar una política
    Given que existe un juego con políticas en el mazo
    And el presidente tiene el poder de propaganda
    When el presidente ejecuta el poder de propaganda
    And decide descartar la política vista
    Then la política debe ser removida del mazo
    And la política debe ser añadida a la pila de descarte

 Scenario: El presidente usa propaganda pero no descarta
   Given que existe un juego con políticas en el mazo
   And el presidente tiene el poder de propaganda
   When decide no descartar la política vista
   And el presidente ejecuta el poder de propaganda
   Then la política debe permanecer en el mazo
   And la pila de descarte no debe cambiar

  Scenario: El presidente intenta usar propaganda sin políticas disponibles
    Given que existe un juego sin políticas en el mazo
    And el presidente tiene el poder de propaganda
    When el presidente ejecuta el poder de propaganda
    Then el poder debe retornar None
    And no debe ocurrir ningún cambio en el estado del juego

  Scenario: El presidente espía las primeras 3 políticas
    Given que existe un juego con al menos 3 políticas en el mazo
    And el presidente tiene el poder de espionaje de políticas
    When el presidente ejecuta el poder de espionaje
    Then debe poder ver las primeras 3 políticas
    And las políticas no deben ser removidas del mazo

  Scenario: El presidente espía políticas cuando hay menos de 3 disponibles
    Given que existe un juego con 2 políticas en el mazo
    And el presidente tiene el poder de espionaje de políticas
    When el presidente ejecuta el poder de espionaje
    Then debe retornar solo las 2 políticas disponibles

  Scenario: El presidente ejecuta a un jugador
    Given que existe un juego con jugadores activos
    And el presidente tiene el poder de ejecución
    And existe un jugador objetivo vivo
    When el presidente ejecuta el poder de ejecución contra el jugador objetivo
    Then el jugador objetivo debe estar marcado como muerto
    And el jugador objetivo debe ser removido de los jugadores activos

  Scenario: El presidente marca a un jugador para ejecución futura
    Given que existe un juego activo
    And el presidente tiene el poder de marcar para ejecución
    And existe un jugador objetivo
    When el presidente marca al jugador objetivo para ejecución
    Then el jugador debe quedar marcado para ejecución
    And el contador fascista actual debe ser registrado

  Scenario: El presidente perdona a un jugador marcado para ejecución
    Given que existe un juego con un jugador marcado para ejecución
    And el presidente tiene el poder de perdón
    When el presidente ejecuta el poder de perdón
    Then el jugador marcado debe ser liberado
    And la marca de ejecución debe ser eliminada

  Scenario: El presidente intenta perdonar sin jugador marcado
    Given que existe un juego sin jugadores marcados para ejecución
    And el presidente tiene el poder de perdón
    When el presidente ejecuta el poder de perdón
    Then el poder debe retornar None
    And debe registrar que no hay jugador marcado

  Scenario: El presidente usa el poder de revelación de partido
    Given que existe un juego con al menos 3 jugadores activos
    And el presidente tiene el poder de revelación
    And existe un canciller objetivo
    When el presidente ejecuta el poder de revelación contra el canciller
    And selecciona un jugador revelador válido
    Then el jugador revelador debe conocer el partido del canciller
    And la información debe ser almacenada correctamente

  Scenario: Falla la revelación por falta de jugadores elegibles
    Given que existe un juego con solo el presidente y canciller activos
    And el presidente tiene el poder de revelación
    When el presidente intenta ejecutar el poder de revelación
    Then el poder debe retornar False
    And no debe ocurrir revelación alguna
