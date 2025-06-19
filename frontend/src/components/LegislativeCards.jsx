import policyLiberal from '../assets/policy-liberal.png';
import policyFascist from '../assets/policy-fascist.png';
import policyBack from '../assets/board-policy.png'; // Fallback visual

const policyIcons = {
  Liberal: policyLiberal,
  Fascist: policyFascist,
};

export default function LegislativeCards({ visible, cards = [], onSelect }) {
  console.log("🃏 Cartas legislativas:", cards);
  if (!visible || !Array.isArray(cards) || cards.length === 0) return null;

  const title =
    cards.length === 3
      ? 'Elija una carta para descartar'
      : cards.length === 2
      ? 'Elija una carta para promulgar'
      : '';

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '1rem',
        zIndex: 9999,
        background: 'rgba(0,0,0,0.3)',
      }}
    >
      {title && (
        <h2 style={{ color: 'white', fontSize: '1.5rem', marginBottom: '1rem' }}>
          {title}
        </h2>
      )}
      <div style={{ display: 'flex', gap: '1rem' }}>
        {cards.map((type, index) => (
          <img
            key={index}
            src={policyIcons[type.charAt(0).toUpperCase() + type.slice(1)] || policyBack}
            alt={`Carta ${index + 1}`}
            style={{
              height: '300px',
              borderRadius: '0.5rem',
              boxShadow: '0 0 10px rgba(0,0,0,0.6)',
              cursor: 'pointer',
              transition: 'transform 0.2s ease-in-out',
            }}
            onClick={() => onSelect(index)}
          />
        ))}
      </div>
    </div>
  );
}
