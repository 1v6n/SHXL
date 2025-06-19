import playerBase from '../assets/player-base.png';
import playerBaseUnselectable from '../assets/player-base-unselectable.png';

export default function ChancellorPicker({
  players,
  currentPlayerId,
  previousChancellorId,
  previousPresidentId,
  onSelect,
  disabled,
}) {
  if (!players || players.length === 0) return null;

  const tooManyPlayers = players.length >= 5;

  const validCandidates = players.filter(p => {
    const isSelf = p.id === currentPlayerId;
    const isDead = p.isAlive === false;
    const isPrevChancellor = p.id === previousChancellorId;
    const isPrevPresident = p.id === previousPresidentId;

    return (
      !isSelf &&
      !isDead &&
      !isPrevChancellor &&
      (!tooManyPlayers || !isPrevPresident)
    );
  });

  return (
    <div
      style={{
        marginTop: '2rem',
        padding: '1rem',
        background: '#222',
        borderRadius: '1rem',
        color: 'white',
        textAlign: 'center',
      }}
    >
      <h3>👑 Eres el Presidente, elige un Canciller:</h3>
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '1rem',
          justifyContent: 'center',
          marginTop: '1rem',
        }}
      >
        {validCandidates.map(p => (
          <div
            key={p.id}
            onClick={() => !disabled && onSelect(p.id)}
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
              cursor: disabled ? 'not-allowed' : 'pointer',
              opacity: disabled ? 0.5 : 1,
              boxShadow: '0 0 6px rgba(0, 0, 0, 0.4)',
              transition: 'transform 0.2s',
            }}
          >
            <img
              src={p.isAlive === false ? playerBaseUnselectable : playerBase}
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