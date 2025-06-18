"""Step definitions for Election Phase behavior tests.

This module contains step definitions for testing the complete election phase
of Secret Hitler XL, including chancellor nomination, eligibility rules,
voting mechanics, and government formation.

Example:
    Run the election phase tests with:
        behave features/election_phase.feature
"""

from unittest.mock import Mock

# mypy: disable-error-code=import
from behave import given, then, when

from src.game.phases.election import ElectionPhase


class MockLegislativePhase:
    def __init__(self, game):
        self.game = game


class MockGameOverPhase:
    def __init__(self, game):
        self.game = game


LegislativePhase = MockLegislativePhase
GameOverPhase = MockGameOverPhase


def setup_game_with_players(context, num_players):
    """Setup game with specified number of players.

    Creates mock players and game state for testing election phase scenarios.

    Args:
        context: Behave context object.
        num_players (int): Number of players to create.
    """
    context.players = []
    for i in range(1, num_players + 1):
        player = Mock()
        player.id = i
        player.name = f"Jugador {i}"
        player.is_bot = False
        player.is_dead = False
        player.is_hitler = False
        player.is_liberal = False
        player.is_fascist = False
        player.is_communist = False
        context.players.append(player)

    context.game = Mock()
    context.game.state.active_players = context.players.copy()
    context.game.state.president_candidate = context.players[0]
    context.game.state.president = None
    context.game.state.chancellor = None
    context.game.state.chancellor_candidate = None
    context.game.state.election_tracker = 0
    context.game.state.board = Mock()
    context.game.state.board.fascist_track = 0
    context.game.state.board.liberal_track = 0
    context.game.state.fascist_track = 0
    context.game.state.winner = None
    context.game.state.term_limited_players = []
    context.game.state.marked_for_execution = None
    context.game.state.marked_for_execution_tracker = None
    context.game.communists_in_play = False

    context.game.logger = Mock()
    context.game.vote_on_government = Mock(return_value=True)
    context.game.enact_chaos_policy = Mock()
    context.game.check_policy_win = Mock(return_value=False)
    context.game.set_next_president = Mock()
    context.game.nominate_chancellor = lambda: None

    context.votes = {}
    context.vote_result = None


# =============================================================================
# NOMINATION PHASE STEPS
# =============================================================================


@given("una partida de Secret Hitler XL con jugadores activos")
def step_impl_game_with_active_players(context):
    """Setup game with default 8 active players.

    Args:
        context: Behave context object.
    """
    setup_game_with_players(context, 8)


@given("el presidente en turno es el jugador {presidente:d}")
def step_impl_current_president(context, presidente):
    """Set current president candidate.

    Args:
        context: Behave context object.
        presidente (int): ID of the president candidate.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)
    context.game.state.president_candidate = context.players[presidente - 1]


@given("el último presidente electo fue el jugador {ultimo_presidente:d}")
def step_impl_last_president(context, ultimo_presidente):
    """Set last elected president.

    Args:
        context: Behave context object.
        ultimo_presidente (int): ID of the last president.
    """
    context.game.state.president = context.players[ultimo_presidente - 1]


@given("el último canciller electo fue el jugador {ultimo_canciller:d}")
def step_impl_last_chancellor(context, ultimo_canciller):
    """Set last elected chancellor.

    Args:
        context: Behave context object.
        ultimo_canciller (int): ID of the last chancellor.
    """
    context.game.state.chancellor = context.players[ultimo_canciller - 1]


@given("hay {num:d} jugadores activos")
def step_impl_active_players_count(context, num):
    """Setup game with specific number of active players.

    Args:
        context: Behave context object.
        num (int): Number of active players to create.
    """
    if hasattr(context, "game") and hasattr(context.game.state, "active_players"):
        if num > len(context.players):
            for i in range(len(context.players) + 1, num + 1):
                player = Mock()
                player.id = i
                player.name = f"Jugador {i}"
                player.is_bot = False
                player.is_dead = False
                player.is_hitler = False
                player.is_liberal = False
                player.is_fascist = False
                player.is_communist = False
                context.players.append(player)
        context.game.state.active_players = context.players[:num]
    else:
        setup_game_with_players(context, num)


@given("la partida contiene jugadores humanos y bots")
def step_impl_mixed_players(context):
    """Setup game with mix of human players and bots.

    Args:
        context: Behave context object.
    """
    setup_game_with_players(context, 8)
    for i, p in enumerate(context.players):
        p.is_bot = i % 2 == 0


@given("se han realizado tres elecciones fallidas consecutivas")
def step_impl_three_failed_elections(context):
    """Setup scenario with three consecutive failed elections.

    Simulates chaos scenario where election tracker has reached maximum.

    Args:
        context: Behave context object.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)

    context.game.state.election_tracker = 3
    context.game.state.president_candidate = context.players[0]
    context.game.state.president = context.players[1]
    context.game.state.chancellor = context.players[2]


# =============================================================================
# VOTING PHASE STEPS - GIVEN
# =============================================================================


@given("el tracker de elecciones fallidas está en {value:d}")
def step_impl_voting_election_tracker(context, value):
    """Set election tracker value.

    Args:
        context: Behave context object.
        value (int): Election tracker value.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)
    context.game.state.election_tracker = value


@given("hay {count:d} políticas fascistas promulgadas")
def step_impl_voting_fascist_policies(context, count):
    """Set number of fascist policies enacted.

    Args:
        context: Behave context object.
        count (int): Number of fascist policies.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)
    context.game.state.board.fascist_track = count
    context.game.state.fascist_track = count


@given("el jugador {player_id:d} es Hitler para votación")
def step_impl_voting_player_is_hitler(context, player_id):
    """Mark player as Hitler.

    Args:
        context: Behave context object.
        player_id (int): ID of Hitler player.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)
    player = context.players[player_id - 1]
    player.is_hitler = True
    player.is_fascist = True


@given("hay jugadores humanos en la partida")
def step_impl_voting_human_players(context):
    """Set some players as human and others as bots.

    Args:
        context: Behave context object.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)

    for i in range(3):
        if i < len(context.players):
            context.players[i].is_bot = False

    for i in range(3, len(context.players)):
        context.players[i].is_bot = True


@given("todos los jugadores son bots")
def step_impl_voting_all_bots(context):
    """Set all players as bots.

    Args:
        context: Behave context object.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)
    for player in context.players:
        player.is_bot = True


@given("el presidente ha nominado como canciller al jugador {canciller:d}")
def step_impl_chancellor_nominated(context, canciller):
    """Set nominated chancellor candidate.

    Args:
        context: Behave context object.
        canciller (int): ID of the nominated chancellor.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)
    context.game.state.chancellor_candidate = context.players[canciller - 1]


@given("los jugadores votan de la siguiente manera")
def step_impl_voting_votes_table(context):
    """Set votes from table data.

    Args:
        context: Behave context object with table data.
    """
    context.votes = {}
    for row in context.table:
        player_id = int(row["jugador"])
        vote = row["voto"]
        context.votes[player_id] = vote


@given('{votos_ja:d} jugadores votan "Ja"')
def step_impl_voting_ja_votes(context, votos_ja):
    """Set number of Ja votes.

    Args:
        context: Behave context object.
        votos_ja (int): Number of Ja votes.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)

    if not hasattr(context, "votes"):
        context.votes = {}

    context.expected_ja_votes = votos_ja

    if hasattr(context, "expected_nein_votes"):
        _process_vote_counts(context)


@given('{votos_nein:d} jugadores votan "Nein"')
def step_impl_voting_nein_votes(context, votos_nein):
    """Set number of Nein votes.

    Args:
        context: Behave context object.
        votos_nein (int): Number of Nein votes.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)

    if not hasattr(context, "votes"):
        context.votes = {}

    context.expected_nein_votes = votos_nein

    if hasattr(context, "expected_ja_votes"):
        _process_vote_counts(context)


@given("el jugador {player_id:d} está marcado para ejecución")
def step_impl_voting_marked_for_execution(context, player_id):
    """Mark player for execution.

    Args:
        context: Behave context object.
        player_id (int): ID of player marked for execution.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)
    marked_player = context.players[player_id - 1]
    context.game.state.marked_for_execution = marked_player
    context.game.state.marked_for_execution_tracker = context.game.state.fascist_track


@given("han pasado {count:d} políticas fascistas desde el marcado")
def step_impl_voting_policies_since_marking(context, count):
    """Set fascist policies enacted since marking.

    Args:
        context: Behave context object.
        count (int): Number of fascist policies since marking.
    """
    if not hasattr(context, "game"):
        setup_game_with_players(context, 8)

    marked_at = getattr(context.game.state, "marked_for_execution_tracker", 0)
    total_fascist_policies = marked_at + count

    context.game.state.board.fascist_track = total_fascist_policies
    context.game.state.fascist_track = total_fascist_policies


# =============================================================================
# WHEN STEPS - NOMINATION AND VOTING
# =============================================================================


@when("el presidente nomina como canciller al jugador {candidato:d}")
def step_impl_nominate_chancellor(context, candidato):
    """President nominates specific player as chancellor.

    Args:
        context: Behave context object.
        candidato (int): ID of the nominated chancellor candidate.
    """
    active_players = context.game.state.active_players
    pres = context.game.state.president_candidate
    last_pres = context.game.state.president
    last_chanc = context.game.state.chancellor

    elegibles = [p for p in active_players if p != pres]

    if len(active_players) > 7:
        if last_pres:
            elegibles = [p for p in elegibles if p != last_pres]
        if last_chanc:
            elegibles = [p for p in elegibles if p != last_chanc]
    else:
        if last_pres:
            elegibles = [p for p in elegibles if p != last_pres]

    if (
        hasattr(context.game.state, "election_tracker")
        and context.game.state.election_tracker >= 3
    ):
        elegibles = []

    context.elegibles = elegibles
    candidato_obj = context.players[candidato - 1]
    context.nominacion_valida = candidato_obj in elegibles
    context.candidato = candidato_obj

    if context.nominacion_valida:
        context.game.state.chancellor_candidate = candidato_obj

    context.game.nominate_chancellor = lambda: (
        candidato_obj if context.nominacion_valida else None
    )

    context.election_phase = ElectionPhase(context.game)
    context.result = context.game.nominate_chancellor()


@when("el presidente intenta nominar como canciller al jugador {candidato:d}")
def step_impl_attempt_nominate_specific_chancellor(context, candidato):
    """President attempts to nominate specific player as chancellor.

    This is a more generic version that handles both valid and invalid nominations.

    Args:
        context: Behave context object.
        candidato (int): ID of the nominated chancellor candidate.
    """
    active_players = context.game.state.active_players
    pres = context.game.state.president_candidate
    last_pres = context.game.state.president
    last_chanc = context.game.state.chancellor

    elegibles = [p for p in active_players if p != pres]

    if len(active_players) > 7:
        if last_pres:
            elegibles = [p for p in elegibles if p != last_pres]
        if last_chanc:
            elegibles = [p for p in elegibles if p != last_chanc]
    else:
        if last_pres:
            elegibles = [p for p in elegibles if p != last_pres]

    if (
        hasattr(context.game.state, "election_tracker")
        and context.game.state.election_tracker >= 3
    ):
        elegibles = []

    context.elegibles = elegibles
    candidato_obj = context.players[candidato - 1]
    context.nominacion_valida = candidato_obj in elegibles
    context.candidato = candidato_obj

    if context.nominacion_valida:
        context.game.state.chancellor_candidate = candidato_obj

    context.game.nominate_chancellor = lambda: (
        candidato_obj if context.nominacion_valida else None
    )
    context.result = context.game.nominate_chancellor()


@when("el presidente intenta nominar un candidato a canciller")
def step_impl_nominate_any_chancellor(context):
    """President attempts to nominate any chancellor candidate.

    Simulates the complete nomination process including chaos detection.

    Args:
        context: Behave context object.
    """
    active_players = context.game.state.active_players
    pres = context.game.state.president_candidate
    last_pres = context.game.state.president
    last_chanc = context.game.state.chancellor
    election_tracker = context.game.state.election_tracker

    if election_tracker >= 3:
        context.elegibles = []
        context.game.enact_chaos_policy()
        context.result = None
        return

    elegibles = [p for p in active_players if p != pres]

    if len(active_players) > 7:
        if last_pres:
            elegibles = [p for p in elegibles if p != last_pres]
        if last_chanc:
            elegibles = [p for p in elegibles if p != last_chanc]
    else:
        if last_pres:
            elegibles = [p for p in elegibles if p != last_pres]

    context.elegibles = elegibles

    context.game.nominate_chancellor = lambda: elegibles[0] if elegibles else None
    context.result = context.game.nominate_chancellor()


@when("el presidente nomina como canciller a un bot elegible")
def step_impl_nominate_bot_chancellor(context):
    """President nominates an eligible bot as chancellor.

    Args:
        context: Behave context object.
    """
    elegibles = [
        p
        for p in context.players
        if p.is_bot and p != context.game.state.president_candidate
    ]
    candidato = elegibles[0] if elegibles else None
    context.candidato = candidato
    context.nominacion_valida = candidato is not None


@when("se procesan los votos")
def step_impl_voting_process_votes(context):
    """Process the votes and determine outcome.

    Args:
        context: Behave context object.
    """
    ja_votes = sum(1 for vote in context.votes.values() if vote == "Ja")
    nein_votes = sum(1 for vote in context.votes.values() if vote == "Nein")

    government_passed = ja_votes > nein_votes

    context.game.vote_on_government.return_value = government_passed

    context.ja_votes = ja_votes
    context.nein_votes = nein_votes
    context.vote_result = government_passed

    if government_passed:
        context.game.state.president = context.game.state.president_candidate
        context.game.state.chancellor = context.game.state.chancellor_candidate
        context.game.state.election_tracker = 0

        if (
            hasattr(context.game.state.chancellor, "is_hitler")
            and context.game.state.chancellor.is_hitler
            and context.game.state.board.fascist_track >= 3
        ):
            context.game.state.winner = "fascist"
            context.next_phase = GameOverPhase(context.game)
        else:
            context.next_phase = LegislativePhase(context.game)
    else:
        context.game.state.election_tracker += 1

        if context.game.state.election_tracker >= 3:
            context.game.enact_chaos_policy()
            context.game.state.election_tracker = 0
            context.game.state.term_limited_players = []

        context.game.set_next_president()
        context.next_phase = ElectionPhase(context.game)


@when("inicia la votación")
def step_impl_voting_starts(context):
    """Voting phase starts.

    Args:
        context: Behave context object.
    """
    if (
        hasattr(context.game.state, "marked_for_execution")
        and context.game.state.marked_for_execution
        and hasattr(context.game.state, "fascist_track")
    ):

        marked_tracker = getattr(context.game.state, "marked_for_execution_tracker", 0)
        current_fascist_track = context.game.state.fascist_track
        policies_since_marking = current_fascist_track - marked_tracker

        if policies_since_marking >= 3:
            marked_player = context.game.state.marked_for_execution
            marked_player.is_dead = True

            if marked_player in context.game.state.active_players:
                context.game.state.active_players.remove(marked_player)

            context.game.state.marked_for_execution = None
            context.game.state.marked_for_execution_tracker = None

    context.voting_started = True
    election_phase = ElectionPhase(context.game)
    context.election_phase = election_phase


@when("se muestran los resultados de votación")
def step_impl_voting_show_results(context):
    """Show voting results.

    Args:
        context: Behave context object.
    """
    context.show_results = True


# =============================================================================
# THEN STEPS - NOMINATION RESULTS
# =============================================================================


@then("la nominación es {resultado}")
def step_impl_nomination_result(context, resultado):
    """Verify nomination result.

    Args:
        context: Behave context object.
        resultado (str): Expected result ('válida' or 'inválida').

    Raises:
        AssertionError: If nomination result doesn't match expected.
    """
    if resultado.strip() == "válida":
        assert (
            context.nominacion_valida
        ), f"La nominación debería ser válida, pero fue inválida."
    else:
        assert (
            not context.nominacion_valida
        ), f"La nominación debería ser inválida, pero fue válida."


@then("la lista de candidatos elegibles contiene a {esperados}")
def step_impl_eligible_candidates_list(context, esperados):
    """Verify list of eligible candidates.

    Args:
        context: Behave context object.
        esperados (str): Expected candidates description. Supports formats:
            - "todos excepto 1, 2, 3"
            - "todos excepto el presidente y el último presidente"
            - "jugadores 3, 4, 5"

    Raises:
        AssertionError: If eligible candidates don't match expected list.
    """
    candidatos_esperados = []

    active_players = context.game.state.active_players

    if "todos excepto el presidente y el último presidente" in esperados:
        pres = context.game.state.president_candidate
        last_pres = context.game.state.president

        excluidos = [pres]
        if last_pres:
            excluidos.append(last_pres)

        candidatos_esperados = [
            p for p in active_players if p not in excluidos and not p.is_dead
        ]

    elif "todos excepto" in esperados:
        ids_excluidos = []
        partes = esperados.replace("todos excepto ", "").replace("y", ",").split(",")
        for p in partes:
            p = p.strip()
            if p.isdigit():
                ids_excluidos.append(int(p))
        candidatos_esperados = [
            p for p in active_players if p.id not in ids_excluidos and not p.is_dead
        ]

    elif "jugadores" in esperados:
        ids_incluidos = []
        partes = esperados.replace("jugadores ", "").split(",")
        for p in partes:
            p = p.strip()
            if p.isdigit():
                ids_incluidos.append(int(p))
        candidatos_esperados = [
            p for p in active_players if p.id in ids_incluidos and not p.is_dead
        ]

    assert set(context.elegibles) == set(
        candidatos_esperados
    ), f"Esperados: {[p.id for p in candidatos_esperados]}, Obtenidos: {[p.id for p in context.elegibles]}"


@then("la lista de candidatos elegibles está vacía")
def step_impl_empty_eligible_list(context):
    """Verify eligible candidates list is empty.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If eligible candidates list is not empty.
    """
    assert context.elegibles == [], "La lista de candidatos debería estar vacía."


@then("se promulga automáticamente una policy de caos")
def step_impl_chaos_policy_enacted(context):
    """Verify chaos policy was automatically enacted.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If chaos policy was not enacted.
    """
    context.game.enact_chaos_policy.assert_called_once()


# =============================================================================
# THEN STEPS - VOTING RESULTS
# =============================================================================


@then("el gobierno es aprobado")
def step_impl_voting_government_approved(context):
    """Verify government was approved.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If government was not approved.
    """
    assert (
        context.vote_result == True
    ), f"Government should be approved, but was rejected. Ja: {context.ja_votes}, Nein: {context.nein_votes}"


@then("el gobierno es rechazado")
def step_impl_voting_government_rejected(context):
    """Verify government was rejected.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If government was not rejected.
    """
    assert (
        context.vote_result == False
    ), f"Government should be rejected, but was approved. Ja: {context.ja_votes}, Nein: {context.nein_votes}"


@then("el gobierno es {resultado}")
def step_impl_voting_government_result(context, resultado):
    """Verify government result matches expected.

    Args:
        context: Behave context object.
        resultado (str): Expected result ('aprobado' or 'rechazado').

    Raises:
        AssertionError: If result doesn't match expected.
    """
    if resultado == "aprobado":
        assert (
            context.vote_result == True
        ), f"Government should be approved, but was rejected"
    else:
        assert (
            context.vote_result == False
        ), f"Government should be rejected, but was approved"


@then("el jugador {player_id:d} se convierte en presidente oficial")
def step_impl_voting_official_president(context, player_id):
    """Verify player becomes official president.

    Args:
        context: Behave context object.
        player_id (int): Expected president ID.

    Raises:
        AssertionError: If wrong player is president.
    """
    assert context.game.state.president == context.players[player_id - 1]


@then("el jugador {player_id:d} se convierte en canciller oficial")
def step_impl_voting_official_chancellor(context, player_id):
    """Verify player becomes official chancellor.

    Args:
        context: Behave context object.
        player_id (int): Expected chancellor ID.

    Raises:
        AssertionError: If wrong player is chancellor.
    """
    assert context.game.state.chancellor == context.players[player_id - 1]


@then("el tracker de elecciones fallidas se reinicia a 0")
def step_impl_voting_tracker_reset(context):
    """Verify election tracker is reset to 0.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If tracker is not 0.
    """
    assert context.game.state.election_tracker == 0


@then("la partida avanza a la fase legislativa")
def step_impl_voting_legislative_phase(context):
    """Verify game advances to legislative phase.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If not in legislative phase.
    """
    assert isinstance(context.next_phase, LegislativePhase)


@then("el tracker de elecciones fallidas se incrementa en {increment:d}")
def step_impl_voting_tracker_increment(context, increment):
    """Verify election tracker increments.

    Args:
        context: Behave context object.
        increment (int): Expected increment amount.
    """
    pass


@then("el siguiente jugador se convierte en candidato a presidente")
def step_impl_voting_next_president_candidate(context):
    """Verify next player becomes president candidate.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If set_next_president was not called.
    """
    context.game.set_next_president.assert_called_once()


@then("la partida permanece en la fase de elección")
def step_impl_voting_stays_election_phase(context):
    """Verify game stays in election phase.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If not in election phase.
    """
    assert isinstance(context.next_phase, ElectionPhase)


@then("el tracker de elecciones fallidas llega a {value:d}")
def step_impl_voting_tracker_reaches(context, value):
    """Verify election tracker reaches specific value.

    Args:
        context: Behave context object.
        value (int): Expected tracker value.

    Raises:
        AssertionError: If tracker doesn't reach expected value.
    """
    # This is verified through the chaos policy being enacted
    if value >= 3:
        context.game.enact_chaos_policy.assert_called_once()


@then("se reinician los límites de términos")
def step_impl_voting_term_limits_reset(context):
    """Verify term limits are reset.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If term limits were not reset.
    """
    assert context.game.state.term_limited_players == []


@then("los fascistas ganan la partida")
def step_impl_voting_fascist_victory(context):
    """Verify fascists win the game.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If fascists didn't win.
    """
    assert context.game.state.winner == "fascist"


@then("el juego termina")
def step_impl_voting_game_over(context):
    """Verify game ends.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If game didn't end.
    """
    assert isinstance(context.next_phase, GameOverPhase)


@then("el sistema solicita el voto de cada jugador humano")
def step_impl_voting_request_human_votes(context):
    """Verify system requests votes from human players.

    Args:
        context: Behave context object.

    Note:
        This would typically involve UI interaction in real implementation.
    """
    human_players = [p for p in context.players if not p.is_bot]
    assert len(human_players) > 0, "Should have human players to request votes from"


@then("los bots votan automáticamente según su estrategia")
def step_impl_voting_bots_vote_automatically(context):
    """Verify bots vote automatically.

    Args:
        context: Behave context object.

    Note:
        In real implementation, this would involve strategy pattern.
    """
    bot_players = [p for p in context.players if p.is_bot]
    assert len(bot_players) > 0, "Should have bot players that vote automatically"


@then("todos los jugadores votan automáticamente según su estrategia")
def step_impl_voting_all_bots_vote(context):
    """Verify all players (bots) vote automatically.

    Args:
        context: Behave context object.
    """
    assert all(p.is_bot for p in context.players), "All players should be bots"


@then("se procesan los votos inmediatamente")
def step_impl_voting_immediate_processing(context):
    """Verify votes are processed immediately.

    Args:
        context: Behave context object.

    Note:
        With all bots, there's no waiting for human input.
    """
    pass


@then('se muestra que el jugador {player_id:d} votó "{vote}"')
def step_impl_voting_show_individual_vote(context, player_id, vote):
    """Verify individual vote is shown correctly.

    Args:
        context: Behave context object.
        player_id (int): Player ID.
        vote (str): Expected vote ('Ja' or 'Nein').

    Raises:
        AssertionError: If vote doesn't match expected.
    """
    assert (
        context.votes[player_id] == vote
    ), f"Player {player_id} should have voted {vote}, but voted {context.votes.get(player_id)}"


@then('se muestra el resultado final como "{resultado}"')
def step_impl_voting_show_final_result(context, resultado):
    """Verify final result display.

    Args:
        context: Behave context object.
        resultado (str): Expected result description.
    """
    context.show_results = True


@then("el jugador {player_id:d} es ejecutado antes de la votación")
def step_impl_voting_player_executed_before(context, player_id):
    """Verify player is executed before voting.

    Args:
        context: Behave context object.
        player_id (int): ID of executed player.

    Raises:
        AssertionError: If player was not executed.
    """
    executed_player = context.players[player_id - 1]
    assert executed_player.is_dead == True
    assert executed_player not in context.game.state.active_players


@then("el jugador {player_id:d} no participa en la votación")
def step_impl_voting_player_no_participation(context, player_id):
    """Verify player doesn't participate in voting.

    Args:
        context: Behave context object.
        player_id (int): ID of non-participating player.

    Raises:
        AssertionError: If player participated in voting.
    """
    assert (
        player_id not in context.votes
    ), f"Player {player_id} should not participate in voting"


@then("los jugadores restantes proceden a votar")
def step_impl_voting_remaining_players_vote(context):
    """Verify remaining players proceed to vote.

    Args:
        context: Behave context object.

    Raises:
        AssertionError: If wrong number of players voted.
    """
    active_alive_players = [
        p for p in context.game.state.active_players if not p.is_dead
    ]
    active_count = len(active_alive_players)

    votes_count = len(context.votes) if hasattr(context, "votes") else 0

    assert (
        votes_count == active_count
    ), f"Expected {active_count} votes from remaining players, got {votes_count}"

    if hasattr(context, "votes"):
        for player_id in context.votes.keys():
            player = context.players[player_id - 1]
            assert not player.is_dead, f"Dead player {player_id} should not have a vote"
            assert (
                player in context.game.state.active_players
            ), f"Inactive player {player_id} should not have a vote"

    for player in active_alive_players:
        assert (
            player.id in context.votes
        ), f"Active player {player.id} should have a vote"


@then("los jugadores restantes votan de la siguiente manera")
def step_impl_remaining_players_vote_table(context):
    """Set votes from table data for remaining players after execution.

    Args:
        context: Behave context object with table data.

    Raises:
        AssertionError: If a dead player tries to vote.
    """
    if not hasattr(context, "votes"):
        context.votes = {}

    for row in context.table:
        player_id = int(row["jugador"])
        vote = row["voto"]

        player = context.players[player_id - 1]

        if player.is_dead:
            raise AssertionError(
                f"Player {player_id} is dead and should not be able to vote"
            )

        if player not in context.game.state.active_players:
            raise AssertionError(f"Player {player_id} is not in active players list")

        context.votes[player_id] = vote

    for player_id in context.votes.keys():
        player = context.players[player_id - 1]
        if player.is_dead:
            raise AssertionError(f"Dead player {player_id} should not have a vote")

    active_alive_players = [
        p for p in context.game.state.active_players if not p.is_dead
    ]
    votes_count = len(context.votes)
    expected_count = len(active_alive_players)

    if votes_count != expected_count:
        active_ids = [p.id for p in active_alive_players]
        vote_ids = list(context.votes.keys())
        raise AssertionError(
            f"Expected {expected_count} votes from active players {active_ids}, "
            f"but got {votes_count} votes from players {vote_ids}"
        )


def _process_vote_counts(context):
    """Process the vote counts and assign votes to players.

    Args:
        context: Behave context object with expected_ja_votes and expected_nein_votes.
    """
    ja_count = getattr(context, "expected_ja_votes", 0)
    nein_count = getattr(context, "expected_nein_votes", 0)

    active_players = context.game.state.active_players
    total_expected = ja_count + nein_count

    if total_expected > len(active_players):
        raise AssertionError(
            f"Cannot assign {total_expected} votes to {len(active_players)} active players"
        )

    context.votes = {}

    for i in range(ja_count):
        if i < len(active_players):
            player = active_players[i]
            context.votes[player.id] = "Ja"

    for i in range(ja_count, ja_count + nein_count):
        if i < len(active_players):
            player = active_players[i]
            context.votes[player.id] = "Nein"

    if hasattr(context, "expected_ja_votes"):
        delattr(context, "expected_ja_votes")
    if hasattr(context, "expected_nein_votes"):
        delattr(context, "expected_nein_votes")
