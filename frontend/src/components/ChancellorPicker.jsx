import playerBase from '../assets/player-base.png';
import playerBaseUnselectable from '../assets/player-base-unselectable.png';
import { useState } from 'react';

export default function ChancellorPicker({
  players,
  currentPlayerId,
  government,
  onSelect,
}) {
  const [selectedId, setSelectedId] = useState(null);

  if (!players || players.length === 0 || !government) return null;

  const termLimitedIds = government.termLimited?.map(p => p.id) ?? [];

  const validCandidates = players.filter(p => {
    const isSelf = p.id === currentPlayerId;
    const isDead = p.isAlive === false;
    const isTermLimited = termLimitedIds.includes(p.id);

    return !isSelf && !isDead && !isTermLimited;
  });

  const handleSelect = (id) => {
    setSelectedId(id);
    onSelect(id);
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'rgba(0,0,0,0.85)',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
        gap: '2rem',
      }}
    >
      <h2>👑 Eres el Presidente, elige un Canciller</h2>
      <div
        style={{
          display: 'flex',
          gap: '1.5rem',
          justifyContent: 'center',
          flexWrap: 'wrap',
        }}
      >
        {validCandidates.map(p => (
          <button
            key={p.id}
            onClick={() => handleSelect(p.id)}
            style={{
              width: '120px',
              height: '180px',
              background: '#181818',
              borderRadius: '0.75rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              cursor: 'pointer',
              boxShadow: selectedId === p.id
                ? '0 0 16px 4px #ffe066, 0 2px 8px rgba(0,0,0,0.5)'
                : '0 2px 8px rgba(0,0,0,0.5)',
              border: 'none',
              outline: selectedId === p.id ? '3px solid #ffe066' : '2px solid #444',
              position: 'relative',
              transition: 'all 0.2s',
              fontSize: '1rem',
              fontWeight: 'bold',
              padding: 0,
            }}
            tabIndex={0}
            onKeyDown={e => {
              if (e.key === 'Enter' || e.key === ' ') {
                handleSelect(p.id);
              }
            }}
          >
            <img
              src={p.isAlive === false ? playerBaseUnselectable : playerBase}
              alt="Jugador"
              style={{
                width: '100px',
                height: '100px',
                marginBottom: '0.75rem',
                filter: p.isAlive === false ? 'grayscale(1)' : 'none',
                opacity: p.isAlive === false ? 0.6 : 1,
                borderRadius: '0%',
                boxShadow: '0 0 8px #000',
              }}
            />
            <span style={{ marginBottom: '0.25rem' }}>{p.name}</span>
            {selectedId === p.id && (
              <span
                style={{
                  position: 'absolute',
                  top: 10,
                  right: 10,
                  background: '#ffe066',
                  color: '#222',
                  borderRadius: '50%',
                  width: 26,
                  height: 26,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '1.2rem',
                  boxShadow: '0 0 4px #ffe066',
                }}
              >✓</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
