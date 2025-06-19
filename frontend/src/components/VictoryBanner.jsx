import { useNavigate } from 'react-router-dom';

import liberalHeader from '../assets/victory-liberal-header.png';
import fascistHeader from '../assets/victory-fascist-header.png';

const banners = {
    Liberal: {
        header: liberalHeader,
    },
    Fascist: {
        header: fascistHeader,
    },
};

export default function VictoryBanner({ winner }) {
    const navigate = useNavigate();

    const normalizedWinner = winner === "Liberales" ? "Liberal" :
                             winner === "Fascistas" ? "Fascist" :
                             winner;

    if (!normalizedWinner || !banners[normalizedWinner]) return null;

    const { header } = banners[normalizedWinner];

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                background: 'rgba(0, 0, 0, 0.9)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '2rem',
                zIndex: 9999,
                gap: '2rem',
            }}
        >
            <img
                src={header}
                alt={`${normalizedWinner} Wins`}
                style={{ maxWidth: '70vw', maxHeight: '35vh', objectFit: 'contain' }}
            />

            <button
                onClick={() => navigate('/')}
                style={{
                    padding: '1rem 2rem',
                    backgroundColor: '#ff5722',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.5rem',
                    fontSize: '1.2rem',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                }}
            >
                Volver al inicio
            </button>
        </div>
    );
}
