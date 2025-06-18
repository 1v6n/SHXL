Feature: Poderes Comunistas
  Como jugador comunista en el juego
  Quiero utilizar los poderes especiales comunistas
  Para obtener ventajas estrategicas en la partida

  Background:
    Given que existe un juego inicializado
    And existen jugadores en la partida
    And hay un presidente asignado
    And hay un canciller asignado

  Scenario: El presidente se confiesa y revela su afiliacion partidaria
    Given que el presidente es comunista
    When el presidente ejecuta el poder "Confession"
    Then la afiliacion del presidente debe ser revelada publicamente
    And la afiliacion revelada debe ser "communist"

  Scenario: Los comunistas espian a otro jugador mediante Bugging
    Given que existen jugadores comunistas en la partida
    And existe un jugador objetivo que no es comunista
    When un comunista ejecuta el poder "Bugging" sobre el jugador objetivo
    Then todos los comunistas deben conocer la afiliacion del jugador objetivo
    And la informacion debe almacenarse en known_affiliations

  Scenario: Se ejecuta el Plan Quinquenal para anadir politicas
    Given que existe un mazo de politicas
    When se ejecuta el poder "FiveYearPlan"
    Then se deben agregar 2 politicas comunistas al mazo
    And se debe agregar 1 politica liberal al mazo
    And las politicas deben estar mezcladas en el mazo

  Scenario: Los comunistas realizan un Congreso para conocerse entre si
    Given que existen multiples jugadores comunistas
    When se ejecuta el poder "Congress"
    Then todos los comunistas deben conocer quienes son los otros comunistas
    And cada comunista debe tener la lista actualizada de comunistas

  Scenario: Radicalizacion exitosa de un jugador liberal
    Given que existe un jugador liberal en la partida
    And el jugador no es Hitler
    When se ejecuta el poder "Radicalization" sobre el jugador liberal
    Then el jugador debe convertirse en comunista
    And el rol del jugador debe cambiar a Communist

  Scenario: Radicalizacion fallida sobre Hitler
    Given que existe un jugador que es Hitler
    When se ejecuta el poder "Radicalization" sobre Hitler
    Then la conversion debe fallar
    And Hitler debe mantener su rol original

  Scenario: Propaganda permite ver la carta superior del mazo
    Given que existe un mazo con politicas disponibles
    And el presidente puede tomar decisiones de propaganda
    When se ejecuta el poder "Propaganda"
    Then se debe mostrar la carta superior del mazo
    And el presidente debe poder decidir si descartarla

  Scenario: Propaganda con decision de descartar la carta
    Given que existe un mazo con politicas disponibles
    And el presidente decide descartar la carta vista
    When se ejecuta el poder "Propaganda"
    Then la carta superior debe ser removida del mazo
    And la carta debe ser enviada a la pila de descarte

  Scenario: Impeachment revela la afiliacion de un jugador a otro
    Given que existe un jugador objetivo
    And existe un jugador revelador
    When se ejecuta el poder "Impeachment" con ambos jugadores
    Then el jugador revelador debe conocer la afiliacion del objetivo
    And la informacion debe guardarse en known_affiliations del revelador

  Scenario: Bugging sobre un jugador que ya es conocido
    Given que un comunista ya conoce la afiliacion de un jugador
    When ejecuta "Bugging" sobre el mismo jugador nuevamente
    Then la informacion debe actualizarse correctamente
    And no debe generar errores de duplicacion
  Scenario: Propaganda con mazo vacio
    Given que el mazo de politicas esta vacio
    When se ejecuta el poder "Propaganda"
    Then debe retornar None
    And no debe generar errores

  Scenario: Radicalizacion exitosa cambia estrategia de jugador liberal con estrategia basada en rol
    Given que existe un jugador liberal en la partida
    And el jugador tiene una estrategia liberal
    And el jugador no es Hitler
    When se ejecuta el poder "Radicalization" sobre el jugador liberal
    Then el jugador debe convertirse en comunista
    And el jugador debe tener una estrategia comunista
    And la estrategia original debe haber sido reemplazada

  Scenario: Radicalizacion exitosa cambia estrategia de jugador fascista con estrategia basada en rol
    Given que existe un jugador fascista en la partida
    And el jugador tiene una estrategia fascista
    And el jugador no es Hitler
    When se ejecuta el poder "Radicalization" sobre el jugador fascista
    Then el jugador debe convertirse en comunista
    And el jugador debe tener una estrategia comunista
    And la estrategia original debe haber sido reemplazada

  Scenario: Radicalizacion no cambia estrategia de jugador con estrategia no basada en rol
    Given que existe un jugador liberal en la partida
    And el jugador tiene una estrategia inteligente
    And el jugador no es Hitler
    When se ejecuta el poder "Radicalization" sobre el jugador liberal
    Then el jugador debe convertirse en comunista
    And el jugador debe mantener su estrategia inteligente
    And la estrategia no debe haber cambiado de tipo

  Scenario: Oktober Fest inicia y todos los bots cambian a estrategia aleatoria
    Given que existe un juego con jugadores bot
    And los jugadores bot tienen estrategias diferentes
    And el contador de mes es 10
    When se ejecuta la transicion de mes
    Then Oktober Fest debe estar activo
    And todos los jugadores bot deben tener estrategia aleatoria
    And las estrategias originales deben estar guardadas

  Scenario: Oktober Fest termina y los bots recuperan sus estrategias originales
    Given que existe un juego con jugadores bot
    And Oktober Fest esta activo
    And los jugadores bot tienen estrategia aleatoria
    And las estrategias originales estan guardadas
    And el contador de mes es 11
    When se ejecuta la transicion de mes
    Then Oktober Fest no debe estar activo
    And todos los jugadores bot deben tener sus estrategias originales
    And las estrategias guardadas deben estar vacias

  Scenario: Oktober Fest no afecta jugadores humanos
    Given que existe un juego con jugadores humanos y bots
    And el contador de mes es 10
    When se ejecuta la transicion de mes
    Then Oktober Fest debe estar activo
    And solo los jugadores bot deben cambiar a estrategia aleatoria
    And los jugadores humanos deben mantener sus estrategias
  Scenario: Oktober Fest no se activa dos veces consecutivas
    Given que existe un juego con jugadores bot
    And Oktober Fest esta activo
    And los jugadores bot tienen estrategia aleatoria
    And el contador de mes es 10
    When se ejecuta la transicion de mes
    Then Oktober Fest debe seguir activo
    And las estrategias no deben cambiar nuevamente
