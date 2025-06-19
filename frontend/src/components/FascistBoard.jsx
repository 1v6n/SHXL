import fascistBoard from '../assets/board-fascist-5-6.png';
import fascistPolicy from '../assets/policy-fascist.png';

const policyPositions = [
  { left: '10.08%', top: '27.5%' },
  { left: '23.6%', top: '27.5%' },
  { left: '37.3%', top: '27.5%' },
  { left: '50.8%', top: '27.5%' },
  { left: '64.5%', top: '27.5%' },
  { left: '78.2%', top: '27.5%' },
];

export default function FacistBoard({ policies = 0})
{
  return (
    <div style={{ position: 'relative', width: '500px' }}>
      {/* Tablero base */}
      <img src={fascistBoard} alt="Tablero fascista" style={{ width: '100%' }} />

      {/* Políticas promulgadas */}
      {[...Array(6)].map((_, i) => (
        i < policies   ? (
          <img
            key={i}
            src={fascistPolicy}
            alt="Política fascista"
            style={{
              position: 'absolute',
              width: '60px',
              left: policyPositions[i].left,
              top: policyPositions[i].top,
              transition: 'opacity 0.3s',
              opacity: 1,
            }}
          />
        ) : null
      ))}
    </div>
  );
}


