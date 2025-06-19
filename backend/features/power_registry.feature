Feature: Registro de Poderes del Juego
    Como desarrollador del juego
    Quiero tener un registro centralizado de todos los poderes
    Para poder gestionar las habilidades especiales de los jugadores

    Background:
        Given que existe una instancia del juego

    Scenario: Obtener poder fascista válido
        When solicito el poder "investigate_loyalty"
        Then debería recibir una instancia de InvestigateLoyalty
        And el poder debería estar asociado al juego

    Scenario: Obtener poder comunista válido
        When solicito el poder "confession"
        Then debería recibir una instancia de Confession
        And el poder debería estar asociado al juego

    Scenario: Obtener poder de Artículo 48 válido
        When solicito el poder "propaganda"
        Then debería recibir una instancia de PresidentialPropaganda
        And el poder debería estar asociado al juego

    Scenario: Obtener poder del Acta Habilitante válido
        When solicito el poder "chancellor_propaganda"
        Then debería recibir una instancia de ChancellorPropaganda
        And el poder debería estar asociado al juego

    Scenario: Error al solicitar poder inexistente
        When solicito el poder "poder_inexistente"
        Then debería recibir un ValueError
        And el mensaje de error debería contener "Unknown power: poder_inexistente"

    Scenario Outline: Identificar propietario de poderes del Canciller
        When consulto el propietario del poder "<poder>"
        Then el propietario debería ser CHANCELLOR

        Examples:
            | poder                              |
            | chancellor_propaganda              |
            | chancellor_impeachment             |
            | chancellor_marked_for_execution    |
            | chancellor_policy_peek             |
            | chancellor_execution               |
            | vote_of_no_confidence              |

    Scenario Outline: Identificar propietario de poderes del Presidente
        When consulto el propietario del poder "<poder>"
        Then el propietario debería ser PRESIDENT

        Examples:
            | poder              |
            | investigate_loyalty|
            | special_election   |
            | policy_peek        |
            | execution          |
            | confession         |
            | propaganda         |
            | impeachment        |
            | pardon             |

    Scenario: Obtener poder aleatorio del Artículo 48
        When solicito un poder aleatorio del Artículo 48
        Then debería recibir un poder válido del Artículo 48
        And el poder debería estar en la lista de poderes presidenciales de emergencia

    Scenario: Obtener poder aleatorio del Acta Habilitante
        When solicito un poder aleatorio del Acta Habilitante
        Then debería recibir un poder válido del Acta Habilitante
        And el poder debería estar en la lista de poderes del canciller de emergencia

    Scenario: Verificar consistencia en el registro de poderes
        When obtengo todos los poderes fascistas disponibles
        Then todos los poderes fascistas deberían ser instanciables
        And cada poder debería tener un propietario válido
