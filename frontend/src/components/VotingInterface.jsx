import jaIcon from '../assets/vote-yes.png';
import neinIcon from '../assets/vote-no.png';

export default function VotingInterface({ visible, onVote }) {
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
        justifyContent: 'center',
        alignItems: 'center',
        gap: '3rem',
        zIndex: 9999,
      }}
    >
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
  );
}