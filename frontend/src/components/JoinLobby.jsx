import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { joinGame } from '../api/gameApi'
import styles from './LobbyForm.module.css';

export default function JoinLobby() {
  const [lobby, setLobby]     = useState('') // Usamos '' porque el lobby es un string
  const [name, setName]       = useState('') // Usamos '' porque el nombre es un string
  const [loading, setLoading] = useState(false) // Usamos false porque al inicio no estamos cargando nada
  const [error, setError]     = useState(null) // Usamos null porque al inicio no hay error
  const navigate = useNavigate()

  const isValid = lobby.trim().length > 7 && name.trim().length > 0 // Validación sencilla: no dejar solo espacios
  // Si el lobby tiene 4 caracteres y el nombre tiene entre 1 y 8 caracteres

  // Handle submit se encarga de manejar el submit del formulario
  const handleSubmit = async e => {
    e.preventDefault() // Evitamos el comportamiento por defecto del formulario
    if (!isValid) { // Si no es válido, no seguimos
      setError('Código de lobby o nombre inválido')
      return
    }

    setError(null) // Reiniciamos el error
    setLoading(true) // Indicamos que estamos cargando
    try {
      const { id: gameId } = await joinGame(lobby.trim(), name.trim())
      navigate(`/game/${gameId}`)
    } catch (err) {
      console.error(err)
      setError('¡No se pudo unir! Por favor, revisa tu código e inténtalo de nuevo.')
    } finally {
      setLoading(false) // Indicamos que hemos terminado de cargar
    }
  }

    const btnClass = !isValid || loading
  ? `${styles.button} ${styles.buttonDisabled}`
  : styles.button;

  // Renderizamos el formulario
  return (
    <div style={{ position: 'relative' }}>
      {/* Cartel en diagonal */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '-50px',
        transform: 'rotate(-45deg)',
        background: 'rgba(255, 0, 0, 0.8)',
        color: 'white',
        padding: '0.5rem 2rem',
        fontWeight: 'bold',
        zIndex: 10,
        pointerEvents: 'none'
      }}>
        PRÓXIMAMENTE
      </div>

      {/* Formulario deshabilitado */}
      <form className={styles.lobbyForm} onSubmit={(e) => e.preventDefault()}>
        <h2 className={styles.heading}>Unirse a Sala</h2>

        <label className={styles.label}>
          Codigo de Sala
          <input
            className={styles.input}
            type="text"
            value=""
            disabled
          />
        </label>

        <label className={styles.label}>
          Nombre
          <input
            className={styles.input}
            type="text"
            value=""
            disabled
          />
        </label>

        <button className={`${styles.button} ${styles.buttonDisabled}`} type="button" disabled>
          Unirse
        </button>
      </form>
    </div>
  )
}
