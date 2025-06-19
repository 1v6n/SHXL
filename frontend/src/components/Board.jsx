import LiberalBoard from './LiberalBoard';
import FascistBoard from './FascistBoard';

import boardDraw from '../assets/board-draw.png';
import boardDiscard from '../assets/board-discard.png';
import boardPolicy from '../assets/board-policy.png'; // Carta visual


export default function Board({
  liberalPolicies,
  fascistPolicies,
  policiesInDeck,
  policiesInDiscard,
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
      <LiberalBoard policies={liberalPolicies} />

      {/* Mazos entre tableros */}
      <div style={{ display: 'flex', gap: '4rem', justifyContent: 'center', alignItems: 'center' }}>
        {/* Mazo */}
        <div style={{ position: 'relative', width: '80px', height: '110px', marginBottom: '2rem' }}>
          {/* Base del mazo */}
          <img
            src={boardDraw}
            alt="Mazo base"
            style={{ height: '120px', position: 'absolute', bottom: 0, left: 0 }}
          />

          {/* Cartas encima del mazo */}
          {[...Array(Math.min(policiesInDeck ?? 0, 25))].map((_, i) => (
            <img
              key={i}
              src={boardPolicy}
              alt="Carta mazo"
              style={{
                position: 'absolute',
                bottom: `${i+7 * 4}px`,
                left: `${i+6 * 2}px`,
                height: '80px',
                zIndex: i + 1,
                opacity: 1
              }}
            />
          ))}

          {/* Texto */}
          <div style={{ position: 'absolute', bottom: '-30px', width: '100%', textAlign: 'center', color: '#ccc' }}>
            Mazo: {policiesInDeck ?? '?'}
          </div>
        </div>

        {/* Descarte */}
        <div style={{ position: 'relative', width: '80px', height: '110px', marginBottom: '2rem' }}>
          {/* Base del descarte */}
          <img
            src={boardDiscard}
            alt="Descarte base"
            style={{ height: '120px', position: 'absolute', bottom: 0, left: 0 }}
          />

          {/* Cartas encima del descarte */}
          {[...Array(Math.min(policiesInDiscard ?? 0, 25))].map((_, i) => (
            <img
              key={i}
              src={boardPolicy}
              alt="Carta descarte"
              style={{
                position: 'absolute',
                bottom: `${i+7 * 4}px`,
                left: `${i+6 * 2}px`,
                height: '80px',
                zIndex: i + 1,
                opacity: 1
              }}
            />
          ))}

          {/* Texto */}
          <div style={{ position: 'absolute', bottom: '-30px', width: '100%', textAlign: 'center', color: '#ccc' }}>
            Descarte: {policiesInDiscard ?? '?'}
          </div>
        </div>
      </div>

      <FascistBoard policies={fascistPolicies} />
    </div>
  );
}