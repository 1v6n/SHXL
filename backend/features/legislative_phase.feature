Feature: Fase legislativa completa - Selección presidencial y promulgación del canciller
  Como presidente electo,
  quiero seleccionar dos políticas de entre tres cartas recibidas,
  para influir en las decisiones legislativas del gobierno y establecer la dirección política de la partida.

  Como canciller,
  quiero poder seleccionar una de las dos políticas recibidas y promulgarla,
  para completar la fase legislativa del gobierno actual y reflejar sus decisiones políticas en el tablero.

  Background:
    Given una partida de Secret Hitler XL activa
    And hay un presidente electo
    And hay un canciller electo
    And la fase legislativa ha comenzado

  # ========== ESCENARIOS DE SELECCIÓN PRESIDENCIAL ==========

  Scenario: Presidente humano selecciona políticas con mazo suficiente
    Given el presidente es un jugador humano
    And el mazo de políticas tiene al menos 3 cartas
    When el presidente recibe 3 cartas de política
    Then se le presentan las 3 cartas al presidente
    And debe seleccionar 1 carta para descartar
    When el presidente descarta una carta
    Then la carta descartada se añade al mazo de descarte
    And las 2 cartas restantes se entregan al canciller

  Scenario: Presidente bot selecciona políticas automáticamente
    Given el presidente es un bot
    And el mazo de políticas tiene al menos 3 cartas
    When el presidente recibe 3 cartas de política
    Then el bot aplica su estrategia para seleccionar el descarte
    And la carta descartada se añade al mazo de descarte
    And las 2 cartas restantes se entregan al canciller

  Scenario: Mazo insuficiente para presidente requiere mezcla
    Given el mazo de políticas tiene menos de 3 cartas
    And el mazo de descarte tiene cartas disponibles
    When el presidente intenta recibir 3 cartas
    Then el mazo de descarte se mezcla con el mazo actual usando board.reshuffle()
    And se forma un nuevo mazo
    And el presidente recibe 3 cartas del nuevo mazo
    And la selección presidencial continúa normalmente

  # ========== ESCENARIOS DE PROMULGACIÓN DEL CANCILLER ==========

  Scenario: Canciller humano promulga política normalmente
    Given el canciller es un jugador humano
    And el canciller ha recibido 2 cartas del presidente
    When el sistema solicita al jugador elegir una carta
    Then se le presentan las 2 cartas al canciller
    And debe seleccionar 1 carta para promulgar
    When el canciller selecciona una carta para promulgar
    Then la carta seleccionada se coloca en el policy tracker correspondiente
    And la carta no seleccionada se envía al mazo de descarte
    And el sistema registra qué tipo de política fue promulgada

  Scenario: Canciller bot promulga política automáticamente
    Given el canciller es un bot
    And el canciller ha recibido 2 cartas del presidente
    When llega el turno del canciller para promulgar
    Then el bot elige mediante su estrategia
    And la carta seleccionada se coloca en el policy tracker correspondiente
    And la carta no seleccionada se envía al mazo de descarte
    And el sistema registra qué tipo de política fue promulgada

  Scenario: Promulgación de emergency power no va al policy tracker
    Given el canciller ha recibido 2 cartas del presidente
    And una de las cartas es de tipo "emergency"
    When el canciller selecciona la carta "emergency" para promulgar
    Then la carta "emergency" NO se coloca en el policy tracker
    And se ejecuta el poder de emergencia correspondiente
    And la carta no seleccionada se envía al mazo de descarte
    And el sistema registra que se promulgó un emergency power

  Scenario: Mazo insuficiente durante entrega al canciller
    Given el presidente ha seleccionado 2 cartas para el canciller
    And hay menos de 2 cartas disponibles en el sistema
    When se intenta entregar las cartas al canciller
    Then se mezcla el mazo de descarte usando board.reshuffle()
    And se continúa con la entrega normalmente

  # ========== ESCENARIOS DE FLUJO COMPLETO ==========

  Scenario: Flujo legislativo completo con jugadores humanos
    Given el presidente es un jugador humano
    And el canciller es un jugador humano
    And el mazo tiene suficientes cartas
    When el presidente recibe 3 cartas de política
    And el presidente descarta 1 carta
    And las 2 cartas restantes se entregan al canciller
    And el sistema solicita al canciller elegir una carta
    And el canciller selecciona 1 carta para promulgar
    Then la carta seleccionada se coloca en el policy tracker correspondiente
    And la carta no seleccionada se envía al mazo de descarte
    And el sistema registra qué tipo de política fue promulgada
    And la fase legislativa se completa exitosamente

  Scenario: Flujo legislativo completo con bots
    Given el presidente es un bot
    And el canciller es un bot
    And el mazo tiene suficientes cartas
    When el presidente recibe 3 cartas de política
    Then el bot presidente aplica su estrategia y descarta 1 carta
    And las 2 cartas restantes se entregan al canciller bot
    When el canciller bot elige mediante su estrategia
    Then la carta seleccionada se coloca en el policy tracker correspondiente
    And la carta no seleccionada se envía al mazo de descarte
    And el sistema registra qué tipo de política fue promulgada

  # ========== ESCENARIOS DE DIFERENTES TIPOS DE POLÍTICA ==========

  Scenario Outline: Promulgación de diferentes tipos de política por el canciller
    Given el canciller ha recibido 2 cartas del presidente
    And una de las cartas es de tipo "<tipo_politica>"
    When el canciller selecciona la carta "<tipo_politica>" para promulgar
    Then la carta se procesa según las reglas de "<tipo_politica>"
    And el policy tracker se actualiza apropiadamente para "<tipo_politica>"
    And el sistema registra la promulgación de "<tipo_politica>"

    Examples:
      | tipo_politica |
      | liberal       |
      | fascista      |
      | comunista     |
      | anti-policy   |
      | emergency     |

  Scenario: Diferentes configuraciones afectan tipos disponibles
    Given la configuración "completa" está activa
    When el presidente recibe 3 cartas
    And el canciller recibe 2 cartas del presidente
    Then las cartas pueden incluir tipos "liberal, fascista, comunista, emergency, anti-policy"
    And el canciller puede promulgar cualquier tipo válido
    And cada tipo se procesa según sus reglas específicas

  # ========== ESCENARIOS DE VALIDACIÓN ==========

  Scenario: Validación de selección presidencial
    Given el presidente ha recibido 3 cartas específicas
    When el presidente intenta descartar una carta
    Then la carta debe estar entre las 3 cartas recibidas
    And solo puede descartar exactamente 1 carta
    And no puede cambiar su decisión una vez confirmada

  Scenario: Validación de selección del canciller
    Given el canciller ha recibido 2 cartas específicas del presidente
    When el canciller intenta seleccionar una carta para promulgar
    Then la carta debe estar entre las 2 cartas recibidas
    And solo puede seleccionar exactamente 1 carta
    And no puede cambiar su decisión una vez confirmada

  # ========== ESCENARIOS DE REGISTRO Y TRANSPARENCIA ==========

  Scenario: Registro detallado de toda la fase legislativa
    Given la fase legislativa está en progreso
    When el presidente descarta una carta
    And el canciller promulga una política específica
    Then se registra la acción del presidente en el log
    And se registra la promulgación del canciller en el log
    And se registra exactamente qué tipo de política fue promulgada
    And se registra el momento de cada acción
    But no se revela a otros jugadores qué cartas específicas fueron descartadas

  Scenario: Visibilidad limitada entre roles
    Given el presidente ha descartado una carta
    And las 2 cartas han sido entregadas al canciller
    When el canciller descarta una carta y promulga otra
    Then el presidente no puede ver qué carta descartó el canciller
    And otros jugadores solo ven la política promulgada en el tablero
    And las cartas descartadas permanecen ocultas para todos
    And solo el tipo de política promulgada es público

  # ========== ESCENARIOS DE ACTUALIZACIÓN DEL TABLERO ==========

  Scenario: Actualización del policy tracker después de promulgación
    Given el canciller ha seleccionado promulgar una política "fascista"
    When la política se coloca en el policy tracker
    Then el policy tracker fascista se incrementa en 1
    And se verifica si se otorgan poderes ejecutivos
    And todos los jugadores pueden ver el nuevo estado del tablero
    And el sistema registra el cambio en el policy tracker

  Scenario: Emergency power no actualiza policy tracker
    Given el canciller ha seleccionado promulgar una carta "emergency"
    When la carta se procesa
    Then la carta NO se coloca en ningún policy tracker
    And se ejecuta el poder de emergencia correspondiente
    And el estado del policy tracker permanece inalterado
    But se registra que se ejecutó un emergency power

  # ========== ESCENARIOS DE FINALIZACIÓN ==========

  Scenario: Transición después de fase legislativa exitosa
    Given el canciller ha promulgado una política
    And el sistema ha registrado la promulgación
    When la fase legislativa se completa
    Then se verifica si hay poderes ejecutivos que activar
    And se comprueban las condiciones de victoria
    And se actualiza el orden de turno para la siguiente ronda
    And se establecen los term limits apropiados
    And se regresa a la fase de elección para el siguiente gobierno
