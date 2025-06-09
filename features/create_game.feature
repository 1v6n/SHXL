Feature: Crear nueva partida

  Scenario: Crear una nueva sala desde el endpoint /newgame
    Given el servidor de juego está en funcionamiento
    When el cliente envía una petición POST a /newgame con 8 jugadores y estrategia "smart"
    Then el sistema responde con estado 201
      And el cuerpo contiene un gameID
      And el estado inicial es "waiting_for_players"
      And la cantidad máxima de jugadores es 8
