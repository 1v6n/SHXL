import { useParams, Link } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { useState } from 'react';
import styles from './Game.module.css';

export default function Game() {
  const { gameId } = useParams();
  const location = useLocation();

  const [players] = useState(() => {
    const playerName = location.state?.playerName;
    return playerName ? [{ name: playerName, vip: true }] : [];
  });

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h2 className={styles.lobbyCode}>LOBBY CODE:</h2>
        <h1 className={styles.lobbyCode}>{gameId?.toUpperCase()}</h1>

        <p style={{ marginTop: '0.5rem', fontSize: '0.95rem', color: '#ccc' }}>
          Copia y comparte este código con otros jugadores para unirse
        </p>

        <input
          type="text"
          value={`http://localhost:5173/game/${gameId}`}
          readOnly
          className={styles.linkInput}
        />

        <div className={styles.playersBox}>
          <h3 style={{ textAlign: 'left', marginBottom: '1rem', color: '#fff' }}>
            Players ({players.length}/10)
          </h3>

          <div className={styles.playersGrid}>
            {players.map((player, index) => (
              <div key={index} className={styles.playerCard}>
                <div className={styles.avatar} />
                <strong>{player.name}</strong>
                {player.vip && <span className={styles.vip}>★ VIP</span>}
              </div>
            ))}
          </div>
        </div>

        <div className={styles.buttonGroup}>
          <Link to="/" className={styles.buttonSecondary}>
            VOLVER AL INICIO
          </Link>
        </div>
      </div>
    </div>
  );
}
