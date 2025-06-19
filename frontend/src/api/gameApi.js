import axios from 'axios';

const API_BASE = 'http://127.0.0.1:5000';  // Ajusta según tu entorno

/**
 * Crea una nueva partida con configuración personalizada.
 *
 * @param {{
 *   playerName: string,
 *   playerCount?: number,
 *   withCommunists?: boolean,
 *   withAntiPolicies?: boolean,
 *   withEmergencyPowers?: boolean,
 *   strategy?: string
 * }} params
 *
 * @returns {Promise<{ gameID: string, maxPlayers: number, state: string, currentPlayers: number }>}
 */
export async function createGame(params) {
  const resp = await axios.post(`${API_BASE}/newgame`, params);
  return resp.data;
}

/**
 * Se une a una partida existente.
 *
 * @param {string} lobbyCode
 * @param {string} playerName
 * @returns {Promise<{ id: string }>}
 */
export async function joinGame(lobbyCode, playerName) {
  const resp = await axios.post(`${API_BASE}/games/${lobbyCode}/join`, { playerName });
  return resp.data;
}
