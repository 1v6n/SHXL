import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createGame, joinGame } from '../api/gameApi';
import styles from './LobbyForm.module.css';

export default function CreateLobby() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfig, setShowConfig] = useState(false);

  const [config, setConfig] = useState({
    playerCount: 6,
    // Los checks ya no están en la vista, pero los valores se mantienen en false
    withCommunists: false,
    withAntiPolicies: false,
    withEmergencyPowers: false,
    strategy: 'smart'
  });

  const navigate = useNavigate();
  const isValid = name.trim().length > 0;

  const handleSubmit = async e => {
    e.preventDefault();
    if (!isValid) {
      setError('Ingresa un nombre válido');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const trimmedName = name.trim();
      // Siempre envía los 3 checks como false
      const { gameID } = await createGame({
        playerName: trimmedName,
        playerCount: config.playerCount,
        withCommunists: false,
        withAntiPolicies: false,
        withEmergencyPowers: false,
        strategy: config.strategy
      });

      const joinResponse = await joinGame(gameID, trimmedName);
      const playerId = joinResponse.playerId;

      navigate(`/game/${gameID}`, {
        state: {
          playerName: trimmedName,
          playerId
        }
      });
    } catch (err) {
      console.error(err);
      setError('Error! Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const btnClass = !isValid || loading
    ? `${styles.button} ${styles.buttonDisabled}`
    : styles.button;

  return (
    <form className={styles.lobbyForm} onSubmit={handleSubmit}>
      <div className={styles.headerRow}>
        <h2 className={styles.heading}>Crear Sala</h2>
        <button
          type="button"
          onClick={() => setShowConfig(prev => !prev)}
          className={styles.gearButton}
          title="Configurar partida"
          disabled={loading}
        >
          ⚙️
        </button>
      </div>

      <label className={styles.label}>
        Nombre
        <input
          className={styles.input}
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          maxLength={8}
          disabled={loading}
        />
      </label>

      {showConfig && (
        <div className={styles.configPanel}>
          <label>
            Cantidad de jugadores:
            <input
              type="number"
              min={5}
              max={6}
              value={config.playerCount}
              onChange={e =>
                setConfig(cfg => ({
                  ...cfg,
                  playerCount: Number(e.target.value)
                }))
              }
              className={styles.numberInput}
              disabled={loading}
            />
          </label>
          <label>
            Estrategia IA:
            <select
              value={config.strategy}
              onChange={e =>
                setConfig(cfg => ({
                  ...cfg,
                  strategy: e.target.value
                }))
              }
              className={styles.selectInput}
              disabled={loading}
            >
              <option value="smart">Smart</option>
              <option value="random">Random</option>
            </select>
          </label>
        </div>
      )}

      {error && <p className={styles.error}>{error}</p>}

      <button className={btnClass} type="submit" disabled={!isValid || loading}>
        {loading ? 'Creando...' : 'Crear Sala'}
      </button>
    </form>
  );
}
