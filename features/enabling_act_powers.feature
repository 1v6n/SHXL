Feature: Poderes del Canciller en el Acta Habilitante
    Como parte del juego Secret Hitler
    Quiero que el Canciller pueda ejercer poderes especiales
    Para influir en el desarrollo del juego

    Background:
        Given que existe un juego inicializado para poderes del Canciller
        And el juego tiene un estado válido con jugadores activos para Canciller
        And hay un Canciller designado para los poderes

    Scenario: Canciller usa propaganda para ver y descartar carta
        Given que hay políticas en el mazo
        And el Canciller tiene el poder de propaganda
        When el Canciller activa el poder de propaganda
        And decide descartar la carta vista
        Then la carta es removida del mazo
        And la carta es añadida a la pila de descarte
        And el poder retorna la política vista

    Scenario: Canciller usa propaganda pero no descarta
        Given que hay políticas en el mazo
        And el Canciller tiene el poder de propaganda
        When el Canciller activa el poder de propaganda
        And decide no descartar la carta vista
        Then la carta permanece en el mazo
        And el poder retorna la política vista

    Scenario: Canciller intenta usar propaganda sin cartas disponibles
        Given que no hay políticas en el mazo
        And el Canciller tiene el poder de propaganda
        When el Canciller usa propaganda con mazo vacío
        Then el poder retorna None
        And no se realizan cambios en el estado del juego

    Scenario: Canciller observa las 3 cartas superiores
        Given que hay al menos 3 políticas en el mazo
        And el Canciller tiene el poder de observación de políticas
        When el Canciller activa el poder de observación
        Then el poder retorna las 3 cartas superiores
        And las cartas permanecen en el mazo en el mismo orden

    Scenario: Canciller observa cartas con menos de 3 disponibles
        Given que hay menos de 3 políticas en el mazo
        And el Canciller tiene el poder de observación de políticas
        When el Canciller activa el poder de observación
        Then el poder retorna todas las cartas disponibles
        And las cartas permanecen en el mazo

    Scenario: Presidente elige a quién revelar la afiliación del Canciller
        Given que hay jugadores elegibles para ver la afiliación
        And el Canciller tiene el poder de impeachment
        And el Presidente debe elegir un revelador
        When el Canciller activa el poder de impeachment
        And el Presidente selecciona un jugador válido
        Then el jugador seleccionado conoce la afiliación del Canciller
        And el poder retorna True

    Scenario: Impeachment con revelador específico proporcionado
        Given que hay un jugador específico como revelador
        And el Canciller tiene el poder de impeachment
        When el Canciller activa impeachment con revelador específico
        Then el revelador conoce la afiliación del Canciller
        And el poder retorna True

    Scenario: Impeachment sin jugadores elegibles
        Given que no hay jugadores elegibles para el impeachment
        And el Canciller tiene el poder de impeachment
        When el Canciller activa el poder de impeachment
        Then el poder retorna False
        And no se revelan afiliaciones

    Scenario: Canciller marca jugador para ejecución
        Given que hay un jugador objetivo válido
        And el Canciller tiene el poder de marcar para ejecución
        When el Canciller activa el marcado para ejecución
        Then el jugador queda marcado para ejecución
        And se registra el estado actual del tracker fascista
        And se genera un log del marcado
        And el poder retorna el jugador marcado

    Scenario: Canciller ejecuta a un jugador
        Given que hay un jugador objetivo para ejecutar
        And el Canciller tiene el poder de ejecución
        When el Canciller activa el poder de ejecución directa
        Then el jugador objetivo es marcado como muerto
        And el jugador es removido de la lista de jugadores activos
        And el poder retorna el jugador ejecutado

    Scenario: Voto de no confianza promulga política descartada
        Given que existe una política previamente descartada
        And el Canciller tiene el poder de voto de no confianza
        When el Canciller activa el voto de no confianza
        Then la última política descartada es promulgada
        And el poder retorna la política promulgada

    Scenario: Voto de no confianza sin política descartada
        Given que no hay política previamente descartada
        And el Canciller tiene el poder de voto de no confianza
        When el Canciller activa el voto de no confianza
        Then el poder retorna None
        And no se promulga ninguna política

    Scenario: Verificar propietario de todos los poderes
        Given cualquier poder del Acta Habilitante
        When se consulta el propietario del poder
        Then el propietario debe ser CHANCELLOR
