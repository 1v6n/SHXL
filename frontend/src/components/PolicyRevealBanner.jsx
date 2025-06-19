import policyLiberal from '../assets/policy-liberal.png';
import policyFascist from '../assets/policy-fascist.png';

const policyImages = {
  liberal: policyLiberal,
  fascist: policyFascist,
};

export default function PolicyRevealBanner({ type }) {
  if (!type || !policyImages[type]) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0,0,0,0.8)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 9999,
        animation: 'fadeInOut 3s ease-in-out',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            color: 'white',
            fontSize: '2rem',
            marginBottom: '2rem',
            textAlign: 'center',
            textShadow: '0 2px 8px rgba(0,0,0,0.7)',
          }}
        >
          El canciller decidió promulgar esta política
        </div>
        <img
          src={policyImages[type]}
          alt={`Política ${type}`}
          style={{
            height: '400px',
            borderRadius: '1rem',
            boxShadow: '0 0 20px rgba(0,0,0,0.8)',
            transition: 'transform 0.5s ease-in-out',
          }}
        />
      </div>
    </div>
  );
}
