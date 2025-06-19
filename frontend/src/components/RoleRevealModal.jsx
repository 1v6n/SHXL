import liberalImg from '../assets/role-liberal-1.png';
import fascistImg from '../assets/role-fascist-2.png';
import hitlerImg from '../assets/role-hitler.png';

const roleAssets = {
  Liberal: liberalImg,
  Fascist: fascistImg,
  Hitler: hitlerImg,
};

const roleDescriptions = {
  Liberal: {
    title: '🟦 Liberal',
    win: 'Ganas si se promulgan 5 políticas liberales o si Hitler es ejecutado.',
    lose: 'Pierdes si Hitler es elegido como Canciller después de 3 políticas fascistas o si se promulgan 6 políticas fascistas.',
    tip: 'Juega de forma honesta, genera confianza y trata de identificar a los fascistas para frenarlos.',
  },
  Fascist: {
    title: '🟥 Fascista',
    win: 'Ganas si Hitler es elegido Canciller después de 3 políticas fascistas o si se promulgan 6 políticas fascistas.',
    lose: 'Pierdes si se promulgan 5 políticas liberales o si Hitler es ejecutado.',
    tip: 'Gana la confianza de los liberales y colabora con otros fascistas para abrirle el camino a Hitler.',
  },
  Hitler: {
    title: '🟥 Hitler',
    win: 'Ganas si eres elegido Canciller después de 3 políticas fascistas o si se promulgan 6 políticas fascistas.',
    lose: 'Pierdes si se promulgan 5 políticas liberales o si eres ejecutado.',
    tip: 'Tu objetivo es confundir, generar confianza y permitir que los fascistas te lleven al poder.',
  },
};

export default function RoleRevealModal({ visible, role, onClose }) {
  if (!visible || !role || !roleAssets[role]) return null;

  const { title, win, lose, tip } = roleDescriptions[role];

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0,0,0,0.85)',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '1rem',
        color: 'white',
        textAlign: 'center',
        padding: '1.5rem',
      }}
    >
      <img
        src={roleAssets[role]}
        alt={`Rol: ${role}`}
        style={{
          maxHeight: '30vh',
          maxWidth: '80vw',
          width: 'auto',
          height: 'auto',
          objectFit: 'contain',
        }}
      />

      <h2 style={{ margin: 0 }}>{title}</h2>
      <p><strong>{win}</strong></p>
      <p><strong>{lose}</strong></p>
      <p style={{ fontStyle: 'italic', color: '#ccc', maxWidth: '500px' }}>{tip}</p>

      <button
        onClick={onClose}
        style={{
          marginTop: '0.5rem',
          padding: '1rem 2.5rem',
          fontSize: '1.25rem',
          fontWeight: 'bold',
          background: '#ff5722',
          color: 'white',
          border: 'none',
          borderRadius: '0.5rem',
          cursor: 'pointer',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        }}
      >
        Entendido
      </button>
    </div>
  );
}
    