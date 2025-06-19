import policyLiberal from '../assets/policy-liberal.png';
import policyFascist from '../assets/policy-fascist.png';
import policyBack from '../assets/board-policy.png';

const policyIcons = {
  Liberal: policyLiberal,
  Fascist: policyFascist,
};

export default function PeekCardsModal({ visible, cards, onClose }) {
  if (!visible || !cards || cards.length !== 3) return null;

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
        gap: '1.5rem',
        color: 'white',
      }}
    >
      <h2>🔍 Próximas 3 cartas del mazo</h2>
      <div style={{ display: 'flex', gap: '1rem' }}>
        {cards.map((type, i) => (
          <img
            key={i}
            src={policyIcons[type] || policyBack}
            alt={`Carta ${type}`}
            style={{
              height: '250px',
              borderRadius: '0.5rem',
              boxShadow: '0 0 10px rgba(0,0,0,0.6)',
            }}
          />
        ))}
      </div>
      <button
        onClick={onClose}
        style={{
          marginTop: '1rem',
          padding: '0.8rem 1.5rem',
          fontSize: '1rem',
          fontWeight: 'bold',
          background: '#ff5722',
          color: 'white',
          border: 'none',
          borderRadius: '0.5rem',
          cursor: 'pointer',
        }}
      >
        Entendido
      </button>
    </div>
  );
}
