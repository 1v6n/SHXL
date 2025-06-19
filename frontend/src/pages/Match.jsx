  import { useEffect, useState, useRef } from 'react';
  import { useParams, useLocation } from 'react-router-dom';
  import {
    getGameState,
    triggerNomination,
    submitVote,
    drawLegislativeCards,
    discardLegislativeCard,
    encactChancellorPolicy,
    submitExecution

  } from '../api/gameApi';

  import GameTable from '../components/GameTable';
  import LegislativeCards from '../components/LegislativeCards';
  import VotingInterface from '../components/VotingInterface';
  import VoteResultBanner from '../components/VoteResultBanner';
  import VictoryBanner from '../components/VictoryBanner';
  import RoleRevealModal from '../components/RoleRevealModal';
  import PolicyRevealBanner from '../components/PolicyRevealBanner';
  import ChancellorPicker from '../components/ChancellorPicker';
  import PeekCardsModal from '../components/PeekCardsModal';
  import ExecutePlayerModal from '../components/ExecutePlayerModal';

  export default function Match() {
    const { gameId } = useParams();
    const location = useLocation();
    const playerId = location.state?.playerId;

    // State es el estado del juego
    const [state, setState] = useState(null);
    // Esto es para manejar errores
    const [error, setError] = useState(null);
    // La última actualización del estado del juego
    const [lastUpdate, setLastUpdate] = useState(null);
    // Es para manejar si el jugador ya votó
    const [hasVoted, setHasVoted] = useState(false);
    // Referencia para saber si el jugador realmente votó
    const reallyHasVoted = useRef(false); // Referencia para saber si el jugador realmente votó
    // Flag para mostrar el resumen de la votación
    const [voteSummary, setVoteSummary] = useState(null);
    // Estado para manejar el ganador
    const [winner, setWinner] = useState(null);
    // Estado para manejar el rol del jugador
    const [myRole, setMyRole] = useState(null);
    // Modal para mostrar el rol del jugador
    const [showRoleModal, setShowRoleModal] = useState(false);
    // Referencia para saber si el rol ya fue revelado
    const alreadyRevealedRole = useRef(false);
    // Estado para manejar el tipo de política promulgada
    const [lastPolicyType, setLastPolicyType] = useState(null);
    // Estado para manejar la selección del canciller
    const [chancellorSelection, setChancellorSelection] = useState(null);
    // Estado para manejar las cartas del presidente
    const [peekCards, setPeekCards] = useState([]);
    // Estado para manejar el modal de ejecución
    const [showExecuteModal, setShowExecuteModal] = useState(false);
    // Estado para manejar si se está esperando la nominación del canciller
    const [awaitingChancellorNomination, setAwaitingChancellorNomination] = useState(false);
    // Estado para manejar las políticas del presidente y canciller
    const [presidentialPolicies, setPresidentialPolicies] = useState([]);
    // Estado para manejar las políticas del canciller
    const [chancellorPolicies, setChancellorPolicies] = useState([]); 
    // Referencia para saber si ya se robaron las políticas
    const alreadyDrewPolicies = useRef(false);
    // Referencia para saber si ya se cargaron las políticas del canciller
    const alreadyLoadedChancellorPolicies = useRef(false);
    // Referencia para saber si se puede apretar el botón de avanzar
    const [canAdvance, setCanAdvance] = useState(true);
    // Referencia para saber si se ha descartado el presidente
    const [presidentDiscarded, setPresidentDiscarded] = useState(false);
    // Referencia para saber si se ha ejecutado el jugador
    const [justEnacted, setJustEnacted] = useState(null); // 'Liberal' o 'Fascist'


    useEffect(() => {
      const fetchState = async () => {
        try {
          const data = await getGameState(gameId, playerId);
          console.log("🧠 Estado completo:", data);
          console.log("🧠 Estado del juego actualizado:", data.currentPhase?.name, "Subfase:", data.currentPhase?.subPhase);
          setState(data);
          // Is President y Is Chancellor son booleanos que indican si el jugador es presidente o canciller
          const isPresident = data.government?.president?.id === playerId;
          const isChancellor = data.government?.chancellor?.id === playerId;

          if (
            (data.currentPhase?.name === 'election' || data.currentPhase?.name === 'setup') &&
            data.government?.president?.id === playerId
          ) {
            setAwaitingChancellorNomination(true);
          }
          if (state?.board && data.currentPhase?.name === 'legislative') {
            const oldLiberal = state.board.liberalPolicies ?? 0;
            const oldFascist = state.board.fascistPolicies ?? 0;
            const newLiberal = data.board.liberalPolicies ?? 0;
            const newFascist = data.board.fascistPolicies ?? 0;
          
            if (newLiberal > oldLiberal) {
              setLastPolicyType('Liberal');
              setTimeout(() => setLastPolicyType(null), 3000);
            } else if (newFascist > oldFascist) {
              setLastPolicyType('Fascist');
              setTimeout(() => setLastPolicyType(null), 3000);
            }
          }
          
          // Mostrar cartel de victoria
          if (data.gameState === 'game_over') {
            const pj = data.government?.chancellorCandidate?.id;
            const chancellorPlayer = data.players?.find(p => p.id === pj);
            // Victoria fascista si Hitler es canciller y hay al menos 3 políticas fascistas
            if (
              chancellorPlayer?.role?.isHitler &&
              (data.board?.fascistPolicies ?? 0) >= 3
            ) {
              setWinner("Fascistas");
            // Victoria Liberal si hay 5 políticas liberales o 6 fascistas
            } else if ((data?.board?.liberalPolicies ?? 0) >= 5) {
              setWinner("Liberales");
            } else if ((data?.board?.fascistPolicies ?? 0) >= 6) {
              setWinner("Fascistas");
            // Victoria Liberal si Hitler está muerto
            } else {
              const hitler = data.players?.find(p => p.role?.isHitler);
              if (hitler && hitler.isAlive === false) {
                setWinner("Liberales");
              }
            }
            return;
          }

          // Si soy el presidente humano, muestro el modal de rol
          const thisPlayer = data.players?.find(p => p.id === playerId);
          if (thisPlayer && thisPlayer.role && !alreadyRevealedRole.current && data.currentPhase?.name === 'setup') { 
            setMyRole(thisPlayer.role.isHitler ? "Hitler" : thisPlayer.role.party.charAt(0).toUpperCase() + thisPlayer.role.party.slice(1));
            setShowRoleModal(true);
            alreadyRevealedRole.current = true;
          }
          // Si soy el presidente humano reseteo el flag de voto
          if (data.currentPhase?.name === 'voting') {
            const currentPlayer = data.players?.find(p => p.id === playerId);
            if (currentPlayer && currentPlayer.hasVoted && !hasVoted) {
              setHasVoted(true);
            }
          }

          // Si soy el presidente humano y estoy en fase legislativa, robo cartas legislativas
          if (
            data.currentPhase?.name === 'legislative' &&
            data.currentPhase?.subPhase === 'draw_policies' &&
            isPresident &&
            !alreadyDrewPolicies.current
          ) {
            alreadyDrewPolicies.current = true;
          
            console.log("🤖 Presidente humano roba cartas legislativas");
            const response = await drawLegislativeCards(gameId);
            console.log("Cartas robadas:", response);
          
            if (response?.drawResult?.policyNames) {
              setPresidentialPolicies(response.drawResult.policyNames); // ✅ ESTA es la fuente de verdad
            }
          }
          console.log("Cartas del canciller:", data.chancellorPolicies);
        // console.log("Soy presidente:", isPresident, "Soy canciller:", isChancellor, "Phase:", data.currentPhase?.name, "Subfase:", data.currentPhase?.subPhase);
        // Si soy canciller y estoy en fase de promulgar políticas, guardo las políticas
          if (
            data.currentPhase?.name === 'legislative' &&
            data.currentPhase?.subPhase === 'chancellor_enact' &&
            isChancellor &&
            !alreadyLoadedChancellorPolicies.current
          ) {
            setHasVoted(false);
            const fallbackPolicies =
              data.chancellorPolicies ??
              data.presidentialChoice?.chosenPolicies;
          
            if (Array.isArray(fallbackPolicies) && fallbackPolicies.length > 0) {
              console.log("✅ Cargando políticas del canciller desde estado");
              setChancellorPolicies(fallbackPolicies);
              alreadyLoadedChancellorPolicies.current = true;
            }
          }



          // Resetear flag si cambia la subfase
          if (data.currentPhase?.subPhase !== 'chancellor_enact') {
            alreadyLoadedChancellorPolicies.current = false;
          }


          if (
            data.currentPhase?.name === 'executive_power' &&
            isPresident &&
            peekCards.length === 0 &&
            data.board.fascistPolicies === 3
          ) {
            const peekResult = await submitExecution(gameId, "policy_peek", null);
            console.log("👀 Presidente humano ve las cartas del mazo:", peekResult);
            setPeekCards(peekResult?.powerExecution?.result?.top_policies);
            if (peekCards) {
              setPeekCards(peekCards);
            }
            console.log("👀 Presidente humano ve las cartas del mazo:", peekResult);
          }


          console.log("Políticas del presidente:",3 > data.board.fascistPolicies);
          if (data.currentPhase?.name === 'executive_power' && isPresident && !showExecuteModal && data.board.fascistPolicies > 3 && data.board.fascistPolicies < 6) {
            setShowExecuteModal(true);
          }

          const extractedWinner = data.currentPhase?.description?.split(":")[1]?.trim();
          setWinner(extractedWinner);

          setLastUpdate(new Date().toLocaleTimeString());
        } catch (err) {
          console.error(err);
          setError('No se pudo cargar el estado del juego');
        }
      };

      fetchState();
      const interval = setInterval(fetchState, 2000);
      return () => clearInterval(interval);
    }, [gameId, playerId, state?.last_vote_result]);

    const handleCloseRoleModal = () => {
      setShowRoleModal(false);

      const isSetup = state?.currentPhase?.name === 'setup';
      const isPresident = state?.government?.president?.id === playerId;

      if (isSetup && isPresident) {
        setAwaitingChancellorNomination(true);
      }else if (state?.currentPhase?.name === 'election' && isPresident) {
        console.log("🟢 Presidente humano inicia nominación");
        setAwaitingChancellorNomination(true);
      }
    };

    const handleChancellorSelection = async (chancellorId) => {
      try {
        await triggerNomination(gameId, chancellorId);
        console.log("✅ Canciller enviado correctamente");
        setChancellorSelection(chancellorId);
        setAwaitingChancellorNomination(false);
      } catch (err) {
        console.error("❌ Error al nominar canciller:", err);
      }
    };

    const handleExecute = async (targetId) => {
      try {
        console.log("🧪 Ejecutar a:", targetId);
        await submitExecution(gameId, "execution", targetId);
        setShowExecuteModal(false);
      } catch (err) {
        console.error("❌ Error al ejecutar jugador:", err?.response?.data || err.message || err);
      }
    };

    const isPresident = state?.government?.president?.id === playerId;
    const isChancellor = state?.government?.chancellor?.id === playerId;
    const isLegislativePhase = state?.currentPhase?.name === 'legislative';
    const showPresidentialCards =
      isLegislativePhase &&
      state?.currentPhase?.subPhase === 'draw_policies' &&
      isPresident;

    const showChancellorCards =
      isLegislativePhase &&
      state?.currentPhase?.subPhase === 'chancellor_enact' &&
      isChancellor;

    const handleAdvance = async () => {
      if (!canAdvance) return;
      setCanAdvance(false);
      try {
        const phase = state?.currentPhase?.name;
        const subPhase = state?.currentPhase?.subPhase;
        const isPresident = state?.government?.president?.id === playerId;
        const isChancellor = state?.government?.chancellor?.id === playerId;
        let finalResult = null;

        if ((phase === 'setup' || phase === 'election') && !isPresident) {
          await triggerNomination(gameId);
        }

        if (phase === 'voting') {
          const botsToVote = state.players.filter(
            (p) => p.isBot && !p.hasVoted
          );

          const yo = state.players.find(p => p.id === playerId);

          if (!reallyHasVoted.current && yo.isAlive) {
            console.log("⛔ Humano no ha votado aún, esperando...");
            setHasVoted(false);
          } else {
            if(!yo.isAlive){
              await submitVote(gameId, yo.id, 'ja');
            }
            for (const bot of botsToVote) {
              const botVote = Math.random() < 0.5 ? 'ja' : 'nein';
              const voteResponse = await submitVote(gameId, bot.id, botVote);
              if (voteResponse?.votingComplete && voteResponse?.electionResult) {
                finalResult = voteResponse;
              }
            }

            if (finalResult) {
              const { passed, jaVotes, neinVotes } = finalResult.electionResult;
              setVoteSummary({ passed, yes: jaVotes, no: neinVotes });
              setTimeout(() => setVoteSummary(null), 3000);

              if (!passed && isPresident) {
                setAwaitingChancellorNomination(true);
                
                console.log("🔁 Nueva nominación por fallar la votación");
              }else if (!passed) {
                console.log("🔁 Nueva nominación por fallar la votación");
                await triggerNomination(gameId, 0);
              }
            }
            reallyHasVoted.current = false;
          }
        }

        if (phase === 'legislative' && subPhase === 'draw_policies' && !isPresident) {
          const response = await drawLegislativeCards(gameId);
          setPresidentDiscarded(true);
          setTimeout(() => setPresidentDiscarded(false), 2000);
          if (isChancellor && response?.presidentialChoice?.chosenPolicies) {
            setChancellorPolicies(response.presidentialChoice.chosenPolicies);
            alreadyLoadedChancellorPolicies.current = true;
          }
        }

        if (phase === 'legislative' && subPhase === 'chancellor_enact' && !isChancellor) {
          alreadyDrewPolicies.current = false;
          const result = await encactChancellorPolicy(gameId, 0);
          const enacted = result.policyResult.enacted;
          console.log("🃏 Política promulgada:", enacted);
          if (enacted === 'liberal' || enacted === 'fascist') {
            setJustEnacted(enacted);
            console.log("🃏 Política promulgada:", enacted);
            setTimeout(() => setJustEnacted(null), 3000);
          }
        }
      } catch (err) {
        console.error("⛔ Error en handleAdvance:", err);
      } finally {
        setTimeout(() => setCanAdvance(true), 3000);
      }
    };



    if (error) return <p style={{ color: 'red' }}>{error}</p>;
    if (!state) return <p style={{ color: 'white' }}>Cargando estado del juego...</p>;

    const currentPlayer = state.players?.find(p => p.id === playerId);
    const isAlive = currentPlayer?.isAlive !== false;

    if (winner === "Fascistas" || winner === "Liberales") {
      return (
        <div style={{ padding: '2rem', color: 'white' }}>
          <VictoryBanner winner={winner} />
        </div>
      );
    }

    return (
      <div style={{ padding: '2rem', color: 'white' }}>
        <h1>🎯 Juego en curso - {gameId.toUpperCase()}</h1>
        <h3>Fase actual: {state.currentPhase?.displayName}</h3>
        <p>Última actualización: {lastUpdate}</p>

        <VictoryBanner winner={winner} />

        {((state.currentPhase?.name === 'election' || state.currentPhase?.name === 'setup' || state.currentPhase?.name === 'voting') && isPresident && awaitingChancellorNomination) && (
          <ChancellorPicker
            players={state.players} 
            currentPlayerId={playerId}
            government={state.government}
            onSelect={handleChancellorSelection}
            disabled={!!chancellorSelection}
          />
        )}

        
        <VotingInterface
          visible={state.currentPhase?.name === 'voting' && !hasVoted && isAlive}
          candidateName={state.government?.chancellorCandidate?.name}
          onVote={async (vote) => {
            if (!isAlive) {
              console.warn("Jugador muerto no puede votar");
              return;
            }
            try {
              const result = await submitVote(gameId, playerId, vote);
              reallyHasVoted.current = true; // Marcamos que el bot realmente votó
              setHasVoted(true);

              const updatedState = await getGameState(gameId, playerId);
              const lastVote = updatedState.last_vote_result;

              if (lastVote && lastVote.votingComplete && !lastVote.passed) {
                const isPresident = updatedState.government?.president?.id === playerId;

                if (updatedState.currentPhase?.name === 'setup' || updatedState.currentPhase?.name === 'election' || updatedState.currentPhase?.name === 'voting') {
                  if (isPresident) {
                    setState(updatedState);
                    setChancellorSelection(null);
                    setAwaitingChancellorNomination(true);
                  } else {
                    await triggerNomination(gameId, 0);
                  }

                // Esperamos y actualizamos el estado para reflejar el nuevo presidente
                setTimeout(async () => {
                  const freshState = await getGameState(gameId, playerId);
                  setState(freshState);
                  if (freshState.government?.president?.id === playerId) {
                    setAwaitingChancellorNomination(true);
                  }
                }, 1000); // le das un segundo al backend para actualizar
                }
              }

            } catch (err) {
              console.error('Error al votar o procesar resultado:', err);
            }
          }}
        />
        
        {isPresident &&
        state.currentPhase?.subPhase === 'draw_policies' &&
        presidentialPolicies.length > 0 && (
          <LegislativeCards
            visible={true}
            cards={presidentialPolicies}
            onSelect={async (index) => {
              try {
                await discardLegislativeCard(gameId, index);
                setPresidentialPolicies([]);
              } catch (err) {
                console.error("Error descartando carta del presidente:", err);
              }
            }}
          />
        )}


      {isChancellor && state.currentPhase?.subPhase === 'chancellor_enact' && chancellorPolicies.length > 0 && (
        <LegislativeCards
          visible={true}
          cards={chancellorPolicies}
          onSelect={async (index) => {
            try {
              console.log("🃏 Canciller elige política en el índice:", index);
              const result = await encactChancellorPolicy(gameId, index);
              const enacted = result?.enactedPolicy;
              if (enacted === 'Liberal' || enacted === 'Fascist') {
                setLastPolicyType(enacted);
                setTimeout(() => setLastPolicyType(null), 3000);
              }
              setChancellorPolicies([]);
            } catch (err) {
              console.error("Error promulgando política del canciller:", err);
            }
          }}
        />
      )}

        
        
        <GameTable
          players={state.players}
          government={state.government}
          board={{
            ...state.board,
            policiesInDeck: state.board.policiesInDeck,
            policiesInDiscard: state.board.policiesInDiscard,
          }}
          playerId={playerId}
        />

        <RoleRevealModal
          visible={showRoleModal}
          role={myRole}
          onClose={handleCloseRoleModal}
        />

        <VoteResultBanner result={voteSummary} />
        <PolicyRevealBanner type={justEnacted} />
        <PeekCardsModal visible={peekCards.length > 0} cards={peekCards} onClose={() => setPeekCards([])} />
        <ExecutePlayerModal
          visible={showExecuteModal}
          players={state.players}
          currentPlayerId={playerId}
          onExecute={handleExecute}
        />

        { presidentDiscarded && (
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            color: 'white',
            padding: '1rem 2rem',
            borderRadius: '1rem',
            fontSize: '1.5rem',
            boxShadow: '0 0 10px rgba(0,0,0,0.5)',
            zIndex: 9999,
            textAlign: 'center'
          }}>
            🗳️ El presidente descartó una política
          </div>
        )}


        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button
            onClick={handleAdvance}
            disabled={!canAdvance}
            style={{
              padding: '1rem 2rem',
              fontSize: '1rem',
              cursor: canAdvance ? 'pointer' : 'not-allowed',
              opacity: canAdvance ? 1 : 0.5
            }}
          >
            Continuar
          </button>
        </div>
      </div>
    );
  }
