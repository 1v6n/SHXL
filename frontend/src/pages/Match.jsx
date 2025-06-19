import { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { getGameState, submitVote, submitLegislativeChoice } from '../api/gameApi';

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

  const [state, setState] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [hasVoted, setHasVoted] = useState(false);
  const [voteSummary, setVoteSummary] = useState(null);
  const [winner, setWinner] = useState(null);
  const [myRole, setMyRole] = useState(null);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [lastPolicyType, setLastPolicyType] = useState(null);
  const [chancellorSelection, setChancellorSelection] = useState(null);
  const [peekCards, setPeekCards] = useState(null);
  const [showExecuteModal, setShowExecuteModal] = useState(false);

  




  useEffect(() => {
    const fetchState = async () => {
      try {
        const data = await getGameState(gameId);
        console.log("🧠 Estado completo:", data);
        setState(data);
        // Detectar si se promulgó una nueva política
        if (state?.board) {
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
        const thisPlayer = data.players?.find(p => p.id === playerId);
        if (thisPlayer && thisPlayer.role && thisPlayer.role !== myRole) {
        setMyRole(thisPlayer.role); // Por ej. "Liberal", "Fascist", "Hitler"
        setShowRoleModal(true);
        }
        // ✅ Mostrar resultado de votación si cambió
        if (
          data.last_vote_result &&
          (!state?.last_vote_result || state.last_vote_result.passed !== data.last_vote_result.passed)
        ) {
          setVoteSummary({
            passed: data.last_vote_result.passed,
            yes: data.last_vote_result.yes_count,
            no: data.last_vote_result.no_count,
          });

          setTimeout(() => {
            setVoteSummary(null);
          }, 3000);
        }

        // ✅ Mostrar modal de proximas politicas
        if (data.currentPhase?.name === 'special_peek' && isPresident && !peekCards) {
          // Asumimos que el backend te manda las cartas en data.peekCards
          setPeekCards(data.peekCards ?? []);
        }
        // ✅ Mostrar modal de ejecución si es la fase de ejecución especial
        if (data.currentPhase?.name === 'special_execute' && isPresident && !showExecuteModal) {
          setShowExecuteModal(true);
        }
        // ✅ Detectar ganador
        if (true) {
          const extractedWinner = data.currentPhase.description?.split(":")[1]?.trim();
          setWinner(extractedWinner);
        }

        // ✅ Timestamp de última actualización
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

  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!state) return <p style={{ color: 'white' }}>Cargando estado del juego...</p>;

  const isLegislativePhase = state.currentPhase?.name === 'legislative';
  const isPresident = state.government?.president?.id === playerId;
  const isChancellor = state.government?.chancellor?.id === playerId;
  const showLegislativeCards = isLegislativePhase && (isPresident || isChancellor);

  const handleChancellorSelection = async (chancellorId) => {
    try {
      await submitChancellorChoice(gameId, playerId, chancellorId); // Asegurate que esté en tu gameApi.js
      setChancellorSelection(chancellorId);
    } catch (err) {
      console.error("Error eligiendo canciller:", err);
    }
  };

  const handleExecute = async (targetId) => {
    try {
      await submitExecutionChoice(gameId, playerId, targetId); // 🔧 debe existir en tu API
      setShowExecuteModal(false);
    } catch (err) {
      console.error("Error al ejecutar jugador:", err);
    }
  };
  return (
    <div style={{ padding: '2rem', color: 'white' }}>
      <h1>🎯 Juego en curso - {gameId.toUpperCase()}</h1>
      <h3>Fase actual: {state.currentPhase?.displayName}</h3>
      <p>Última actualización: {lastUpdate}</p>

      {state.currentPhase?.name === 'voting' && state.government?.chancellor?.name && (
        <div style={{
          fontSize: '1.4rem',
          background: '#222',
          padding: '1rem 2rem',
          borderRadius: '1rem',
          textAlign: 'center',
          marginBottom: '1rem',
          color: '#fff'
        }}>
          🗳️ Votando a <strong>{state.government.chancellor.name}</strong> como Canciller
        </div>
      )}

      {state.currentPhase?.name === 'choose_chancellor' && isPresident && (
        <ChancellorPicker
          players={state.players}
          currentPlayerId={playerId}
          previousChancellorId={state.board.previousChancellorId}
          previousPresidentId={state.board.previousPresidentId}
          onSelect={handleChancellorSelection}
          disabled={!!chancellorSelection}
        />
      )}

      <VotingInterface
        visible={state.currentPhase?.name === 'voting' && !hasVoted}
        onVote={async (vote) => {
          try {
            await submitVote(gameId, playerId, vote);
            setHasVoted(true);
          } catch (err) {
            console.error('Error al votar:', err);
          }
        }}
      />

      <LegislativeCards
        visible={showLegislativeCards}
        cards={state.policiesToChoose ?? []}
        onSelect={async (index) => {
          try {
            await submitLegislativeChoice(gameId, playerId, index);
            console.log("Carta seleccionada enviada");
          } catch (err) {
            console.error('Error enviando selección legislativa:', err);
          }
        }}
      />

      <GameTable
        players={state.players}
        board={{
          ...state.board,
          policiesInDeck: state.board.policiesInDeck,
          policiesInDiscard: state.board.policiesInDiscard,
        }}
      />
      
      <RoleRevealModal
        visible={showRoleModal}
        role={myRole}
        onClose={() => setShowRoleModal(false)}
      />

      <VoteResultBanner result={voteSummary} />

      <PolicyRevealBanner type={lastPolicyType} />
      
      <PeekCardsModal
        visible={!!peekCards}
        cards={peekCards}
        onClose={() => setPeekCards(null)}
      />

      <ExecutePlayerModal
        visible={showExecuteModal}
        players={state.players}
        currentPlayerId={playerId}
        onExecute={handleExecute}
      />
      
      <VictoryBanner winner={winner} />
    </div>
  );
}