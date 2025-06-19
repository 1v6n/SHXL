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
    playerCount: 10,
    withCommunists: true,
    withAntiPolicies: true,
    withEmergencyPowers: true,
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
      const { gameID } = await createGame({ playerName: name.trim(), ...config });
      await joinGame(gameID, trimmedName);
      navigate(`/game/${gameID}`, { state: { playerName: trimmedName } });
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
              max={10}
              value={config.playerCount}
              onChange={e => setConfig({ ...config, playerCount: parseInt(e.target.value) })}
              className={styles.numberInput}
            />
          </label>
          <label><input type="checkbox" checked={config.withCommunists} onChange={e => setConfig({ ...config, withCommunists: e.target.checked })} /> Incluir comunistas</label>
          <label><input type="checkbox" checked={config.withAntiPolicies} onChange={e => setConfig({ ...config, withAntiPolicies: e.target.checked })} /> Incluir políticas anti</label>
          <label><input type="checkbox" checked={config.withEmergencyPowers} onChange={e => setConfig({ ...config, withEmergencyPowers: e.target.checked })} /> Incluir poderes de emergencia</label>
          <label>
            Estrategia IA:
            <select
              value={config.strategy}
              onChange={e => setConfig({ ...config, strategy: e.target.value })}
              className={styles.selectInput}
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
