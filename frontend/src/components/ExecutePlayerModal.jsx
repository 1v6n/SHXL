import playerBase from '../assets/player-base.png';
import playerBaseUnselectable from '../assets/player-base-unselectable.png';

export default function ExecutePlayerModal({ visible, players, currentPlayerId, onExecute }) {
  if (!visible || !players) return null;

  const candidates = players.filter(p => p.isAlive && p.id !== currentPlayerId);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0,0,0,0.85)',
        zIndex: 9999,
        color: 'white',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: '3rem',
        gap: '1rem',
      }}
    >
      <h2>☠️ Elige a un jugador para ejecutar</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', justifyContent: 'center' }}>
        {candidates.map(p => (
          <div
            key={p.id}
            onClick={() => onExecute(p.id)}
            style={{
              width: '90px',
              height: '120px',
              background: '#333',
              borderRadius: '0.5rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0.5rem',
              color: 'white',
              cursor: 'pointer',
              boxShadow: '0 0 6px rgba(0, 0, 0, 0.4)',
              transition: 'transform 0.2s',
            }}
          >
            <img
              src={playerBase}
              alt="Jugador"
              style={{ width: '50px', height: '50px', marginBottom: '0.5rem' }}
            />
            <strong style={{ fontSize: '0.75rem' }}>{p.name}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
