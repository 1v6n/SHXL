import liberalBoard from '../assets/board-liberal.png';
import liberalPolicy from '../assets/policy-liberal.png';
import trackerToken from '../assets/board-tracker.png';

const policyPositions = [
  { left: '17.08%', top: '27%' },
  { left: '30.58%', top: '27%' },
  { left: '44.18%', top: '27%' },
  { left: '57.75%', top: '27%' },
  { left: '71.6%', top: '27%' },
];

const trackerPositions = [
  { left: '34.69%' },
  { left: '43.98%' },
  { left: '53.18%' },
  { left: '62.38%' },
];

export default function LiberalBoard({ policies = 0, failedElections = 0 }) {
  return (
    <div style={{ position: 'relative', width: '500px' }}>
      {/* Tablero base */}
      <img src={liberalBoard} alt="Tablero liberal" style={{ width: '100%' }} />

      {/* Políticas promulgadas */}
      {[...Array(5)].map((_, i) => (
        i < policies ? (
          <img
            key={i}
            src={liberalPolicy}
            alt="Política liberal"
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

      {/* Ficha del tracker */}
      {failedElections >= 0 && failedElections <= 3 && (
        <img
          src={trackerToken}
          alt="Ficha tracker"
          style={{
            position: 'absolute',
            top: '74.82%',
            left: trackerPositions[failedElections].left,
            width: '2%',
            transition: 'left 0.3s',
            zIndex: 2,
          }}
        />
      )}
    </div>
  );
}