import { useParams, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getGameState } from '../api/gameApi';

export default function Match() {
  const { gameId } = useParams();
  const location = useLocation();
  const playerId = location.state?.playerId; // <- en el futuro lo usarás

  const [gameState, setGameState] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchState = async () => {
      try {
        const state = await getGameState(gameId); // podrías pasar playerId como query param si lo necesitás
        console.log("🧠 Estado completo:", state); // 👈 línea clave
        setGameState(state);
      } catch (err) {
        console.error('Error obteniendo estado del juego:', err);
        setError('No se pudo obtener el estado del juego');
      }
    };

    fetchState();
    const interval = setInterval(fetchState, 2000);
    return () => clearInterval(interval);
  }, [gameId]);

  if (error) {
    return <div style={{ color: 'red', padding: '1rem' }}>{error}</div>;
  }

  if (!gameState) {
    return <div style={{ padding: '1rem', color: 'white' }}>Cargando estado del juego...</div>;
  }

  return (
    <div style={{ padding: '2rem', color: 'white' }}>
      <h1>🎮 Juego en curso</h1>
      <p><strong>Game ID:</strong> {gameId}</p>
      <p><strong>Estado:</strong> {gameState.gameState}</p>
      <p><strong>Fase:</strong> {gameState.currentPhase?.displayName}</p>

      <h2>Jugadores</h2>
      <ul>
        {gameState.players.map((p) => (
          <li key={p.id}>
            {p.name} {p.isBot && '🤖'} {p.playerType === 'human' && p.id === playerId && '🧍 (yo)'}
          </li>
        ))}
      </ul>
    </div>
  );
}