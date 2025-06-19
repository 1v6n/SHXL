import jaIcon from '../assets/vote-yes.png';
import neinIcon from '../assets/vote-no.png';

export default function VotingInterface({ visible, onVote, candidateName }) {
  if (!visible) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'rgba(0, 0, 0, 0.4)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '2rem',
        zIndex: 9999,
      }}
    >
      <div style={{ color: 'white', fontSize: '2rem', marginBottom: '1rem', textAlign: 'center' }}>
        ¿Votas para que <b>{candidateName}</b> sea el canciller?
      </div>
      <div style={{ display: 'flex', gap: '3rem' }}>
        <img
          src={jaIcon}
          alt="JA"
          style={{ height: '200px', cursor: 'pointer' }}
          onClick={() => onVote('ja')}
        />
        <img
          src={neinIcon}
          alt="NEIN"
          style={{ height: '200px', cursor: 'pointer' }}
          onClick={() => onVote('nein')}
        />
      </div>
    </div>
  );
}
