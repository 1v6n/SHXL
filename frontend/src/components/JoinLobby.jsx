import styles from './LobbyForm.module.css';

export default function JoinLobby() {
  return (
    <div className={styles.lobbyForm} style={{ opacity: 0.6, pointerEvents: 'none', position: 'relative' }}>
      <h2 className={styles.heading}>Unirse a Sala</h2>
      <label className={styles.label}>
        Código de Sala
        <input className={styles.input} type="text" disabled />
      </label>
      <label className={styles.label}>
        Nombre
        <input className={styles.input} type="text" disabled />
      </label>
      <button className={styles.button} type="button" disabled>
        Unirse
      </button>
      <p
        style={{
          position: 'absolute',
          top: 8,
          left: 8,
          color: '#fff',
          fontStyle: 'italic',
          margin: 0,
          background: '#e53935',
          padding: '2px 16px',
          borderRadius: 4,
          fontSize: 14,
          transform: 'rotate(-12deg)',
          fontWeight: 'bold',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        }}
      >
        Próximamente
      </p>
    </div>
  );
}
