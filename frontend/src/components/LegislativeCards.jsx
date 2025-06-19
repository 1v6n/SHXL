import policyLiberal from '../assets/policy-liberal.png';
import policyFascist from '../assets/policy-fascist.png';
import policyBack from '../assets/board-policy.png'; // Fallback visual

const policyIcons = {
  Liberal: policyLiberal,
  Fascist: policyFascist,
};

export default function LegislativeCards({ visible, cards = [], onSelect }) {
  if (!visible || !Array.isArray(cards) || cards.length === 0) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '1rem',
        zIndex: 9999,
        background: 'rgba(0,0,0,0.3)',
      }}
    >
      {cards.map((type, index) => (
        <img
          key={index}
          src={policyIcons[type] || policyBack}
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
  );
}