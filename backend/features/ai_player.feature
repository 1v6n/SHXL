Feature: Funcionalidad del jugador AI

  Como jugador AI,
  quiero usar estrategias automatizadas para tomar decisiones,
  para jugar de manera inteligente y consistente con mi rol.

  Background:
    Given un estado de juego mock configurado

  # Initialization scenarios
  Scenario: Inicialización de jugador AI con rol liberal y estrategia por defecto
    Given un jugador AI con ID 1, nombre "AI Liberal", role "liberal", y estrategia "role"
    Then el jugador AI debe tener ID 1
    And el jugador AI debe tener nombre "AI Liberal"
    And el jugador AI debe tener role "liberal"
    And el jugador AI debe usar estrategia LiberalStrategy
    And debe heredar propiedades de Player abstracto

  Scenario: Inicialización de jugador AI con rol fascista y estrategia por defecto
    Given un jugador AI con ID 2, nombre "AI Fascist", role "fascist", y estrategia "role"
    Then el jugador AI debe tener ID 2
    And el jugador AI debe usar estrategia FascistStrategy

  Scenario: Inicialización de jugador AI con rol comunista y estrategia por defecto
    Given un jugador AI con ID 3, nombre "AI Communist", role "communist", y estrategia "role"
    Then el jugador AI debe usar estrategia CommunistStrategy

  Scenario: Inicialización de jugador AI con rol hitler y estrategia por defecto
    Given un jugador AI con ID 4, nombre "AI Hitler", role "hitler", y estrategia "role"
    Then el jugador AI debe usar estrategia FascistStrategy

  Scenario: Inicialización de jugador AI con estrategia random
    Given un jugador AI con ID 5, nombre "AI Random", role "liberal", y estrategia "random"
    Then el jugador AI debe usar estrategia RandomStrategy

  Scenario: Inicialización de jugador AI con estrategia smart
    Given un jugador AI con ID 6, nombre "AI Smart", role "fascist", y estrategia "smart"
    Then el jugador AI debe usar estrategia SmartStrategy

  Scenario: Inicialización de jugador AI con rol nulo
    Given un jugador AI con ID 7, nombre "AI NoRole", role nulo, y estrategia "role"
    Then el jugador AI debe usar estrategia RandomStrategy

  Scenario: Inicialización de jugador AI con rol como string
    Given un jugador AI con ID 8, nombre "AI String", role string "liberal", y estrategia "role"
    Then el jugador AI debe convertir el string a objeto Liberal
    And el jugador AI debe usar estrategia LiberalStrategy

  # Chancellor nomination scenarios
  Scenario: Nominación de canciller con jugadores elegibles predefinidos
    Given un jugador AI liberal configurado
    And hay 3 jugadores elegibles para canciller con IDs 2, 3, 4
    When el jugador AI nomina un canciller
    Then debe delegar la decisión a la estrategia LiberalStrategy
    And debe retornar un jugador de los elegibles

  Scenario: Nominación de canciller sin jugadores elegibles predefinidos
    Given un jugador AI fascista configurado
    And el estado del juego tiene jugadores elegibles para canciller
    When el jugador AI nomina un canciller sin lista predefinida
    Then debe obtener jugadores elegibles del estado
    And debe delegar la decisión a la estrategia FascistStrategy

  # Policy filtering scenarios
  Scenario: Filtrar políticas como presidente AI liberal
    Given un jugador AI liberal configurado
    And 3 políticas disponibles: "liberal", "fascist", "communist"
    When el jugador AI filtra las políticas
    Then debe delegar la decisión a la estrategia LiberalStrategy
    And debe retornar 2 políticas elegidas y 1 descartada

  Scenario: Filtrar políticas como presidente AI fascista
    Given un jugador AI fascista configurado
    And 3 políticas disponibles: "fascist", "liberal", "communist"
    When el jugador AI filtra las políticas
    Then debe delegar la decisión a la estrategia FascistStrategy
    And debe retornar 2 políticas elegidas y 1 descartada

  # Policy choice scenarios
  Scenario: Elegir política como canciller AI comunista
    Given un jugador AI comunista configurado
    And 2 políticas disponibles: "communist", "liberal"
    When el jugador AI elige una política
    Then debe delegar la decisión a la estrategia CommunistStrategy
    And debe retornar 1 política elegida y 1 descartada

  Scenario: Elegir política como canciller AI con estrategia smart
    Given un jugador AI con estrategia smart configurado
    And 2 políticas disponibles: "fascist", "liberal"
    When el jugador AI elige una política
    Then debe delegar la decisión a la estrategia SmartStrategy

  # Voting scenarios
  Scenario: Votación de gobierno AI liberal
    Given un jugador AI liberal configurado
    And un presidente candidato en el estado
    And un canciller candidato en el estado
    When el jugador AI vota en el gobierno
    Then debe delegar la decisión a la estrategia LiberalStrategy
    And debe retornar True o False

  Scenario: Votación de gobierno AI con estrategia random
    Given un jugador AI con estrategia random configurado
    And candidatos configurados en el estado
    When el jugador AI vota en el gobierno
    Then debe delegar la decisión a la estrategia RandomStrategy

  # Veto scenarios
  Scenario: Decisión de veto como canciller AI
    Given un jugador AI fascista configurado
    And políticas actuales en el estado para veto
    When el jugador AI decide sobre veto
    Then debe delegar la decisión a la estrategia FascistStrategy
    And debe retornar True o False

  Scenario: Aceptación de veto como presidente AI
    Given un jugador AI liberal configurado
    And políticas actuales en el estado para aceptar veto
    When el jugador AI decide aceptar veto
    Then debe delegar la decisión a la estrategia LiberalStrategy

  # Policy viewing scenarios
  Scenario: Ver políticas con Policy Peek
    Given un jugador AI configurado
    And 3 políticas para mostrar: "liberal", "fascist", "communist"
    When el jugador AI ve las políticas
    Then debe guardar las políticas en peeked_policies
    And las políticas guardadas deben coincidir con las mostradas

  # Execution scenarios
  Scenario: Ejecutar jugador inmediatamente
    Given un jugador AI comunista configurado
    And 4 jugadores activos en el estado
    When el jugador AI elige un jugador para ejecutar
    Then debe filtrar jugadores eligibles excluyendo a sí mismo
    And debe delegar la decisión a la estrategia CommunistStrategy

  Scenario: Marcar jugador para ejecución
    Given un jugador AI fascista configurado
    And jugadores activos disponibles
    When el jugador AI marca un jugador para ejecución
    Then debe delegar la decisión a la estrategia FascistStrategy

  # Inspection scenarios
  Scenario: Inspeccionar jugador con jugadores no inspeccionados
    Given un jugador AI liberal configurado
    And jugadores activos en el estado
    And el jugador AI no ha inspeccionado a nadie
    When el jugador AI inspecciona un jugador
    Then debe filtrar jugadores no inspeccionados
    And debe delegar la decisión a la estrategia LiberalStrategy

  # Special election scenarios
  Scenario: Elegir siguiente presidente en elección especial
    Given un jugador AI fascista configurado
    And jugadores activos disponibles para presidencia
    When el jugador AI elige el siguiente presidente
    Then debe filtrar jugadores eligibles excluyendo a sí mismo
    And debe delegar la decisión a la estrategia FascistStrategy

  # Radicalization scenarios
  Scenario: Radicalizar jugador a comunista
    Given un jugador AI comunista configurado
    And jugadores elegibles para radicalización
    When el jugador AI elige un jugador para radicalizar
    Then debe filtrar jugadores excluyendo a sí mismo y Hitler
    And debe delegar la decisión a la estrategia CommunistStrategy

  # Propaganda scenarios

  Scenario: Decisión de propaganda - jugador fascista descarta liberal
    Given un jugador AI fascista configurado
    And una política liberal como top policy
    When el jugador AI decide sobre propaganda
    Then debe retornar True para descartar política liberal

  Scenario: Decisión de propaganda - comportamiento por defecto
    Given un jugador AI con rol desconocido configurado
    And una política cualquiera como top policy
    When el jugador AI decide sobre propaganda
    Then debe retornar False

  # Impeachment scenarios

  Scenario: Elegir revelador para impeachment - jugador fascista
    Given un jugador AI fascista configurado
    And jugadores fascistas conocidos
    When el jugador AI elige un revelador
    Then debe preferir jugadores fascistas conocidos

  # Social Democratic scenarios

  # Pardon scenarios
  Scenario: Perdonar jugador - fascista perdona a Hitler
    Given un jugador AI fascista configurado
    And Hitler está marcado para ejecución
    When el jugador AI decide sobre perdón
    Then debe retornar True para perdonar a Hitler

  Scenario: Perdonar jugador - sin estrategia de perdón implementada
    Given un jugador AI con estrategia sin método pardon configurado
    And un jugador marcado para ejecución
    When el jugador AI decide sobre perdón
    Then debe usar lógica de fallback
    And debe retornar False por defecto

  # Bug scenarios
  Scenario: Elegir jugador para espiar
    Given un jugador AI smart configurado
    And jugadores elegibles para espionaje
    When el jugador AI elige un jugador para espiar
    Then debe delegar la decisión a la estrategia SmartStrategy

  # Chancellor veto proposal scenarios
  Scenario: Propuesta de veto del canciller
    Given un jugador AI liberal configurado
    And veto está disponible en el estado
    And políticas disponibles para veto
    When el jugador AI propone veto como canciller
    Then debe delegar la decisión a la estrategia LiberalStrategy

  Scenario: Propuesta de veto del canciller sin veto disponible
    Given un jugador AI configurado
    And veto no está disponible en el estado
    When el jugador AI propone veto como canciller
    Then debe retornar False

  # Vote of no confidence scenarios
  Scenario: Voto de no confianza
    Given un jugador AI fascista configurado
    When el jugador AI decide sobre voto de no confianza
    Then debe delegar la decisión a la estrategia FascistStrategy

  # Duplicate method scenarios for comprehensive coverage
  Scenario: Marcar jugador para ejecución con lista predefinida
    Given un jugador AI liberal configurado
    And una lista específica de jugadores elegibles para marcar
    When el jugador AI marca un jugador con lista predefinida
    Then debe usar la lista proporcionada
    And debe delegar la decisión a la estrategia LiberalStrategy

  Scenario: Marcar jugador para ejecución sin lista predefinida
    Given un jugador AI comunista configurado
    And jugadores activos en el estado
    When el jugador AI marca un jugador sin lista predefinida
    Then debe usar jugadores activos excluyendo a sí mismo
    And debe delegar la decisión a la estrategia CommunistStrategy

  Scenario: Elegir a quien perdonar usando método choose_to_pardon
    Given un jugador AI fascista configurado
    When el jugador AI elige perdonar usando método alternativo
    Then debe delegar la decisión a la estrategia FascistStrategy

  Scenario: Investigar jugador usando método específico
    Given un jugador AI liberal configurado
    And jugadores elegibles para investigación
    When el jugador AI investiga usando método específico
    Then debe delegar la decisión a la estrategia LiberalStrategy

  Scenario: Elegir siguiente presidente usando método específico
    Given un jugador AI comunista configurado
    And jugadores elegibles para presidencia especial
    When el jugador AI elige presidente usando método específico
    Then debe delegar la decisión a la estrategia CommunistStrategy
