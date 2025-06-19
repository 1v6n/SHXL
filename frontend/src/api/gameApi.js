// src/api/gameApi.jsAdd commentMore actions
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

export async function getGameState(gameID) {
  const resp = await axios.get(`${API_BASE}/games/${gameID}/state`);
  return resp.data;
}

export async function addBots(gameID, count = 1, strategy = 'smart', namePrefix = 'Bot') {
  const resp = await axios.post(`${API_BASE}/games/${gameID}/add-bots`, {
    count,
    strategy,
    namePrefix
  });
  return resp.data;
}

/**
 * Obtiene la lista de partidas disponibles.
 * 
 * @returns {Promise<Array<{ id: string, maxPlayers: number, currentPlayers: number, state: string }>>}
 */
export async function startGame(gameId) {
  const response = await fetch(`http://localhost:5000/games/${gameId}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hostPlayerID: 0 })  // por ahora el host siempre es el ID 0
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Unknown error');
  }

  return await response.json();
}

export async function submitVote(gameId, playerId, vote) {
    console.log("🗳️ Enviando voto:", { gameId, playerId, vote });
  const response = await axios.post(`${API_BASE}/games/${gameId}/vote`, {
    playerId: playerId,
    vote: vote.toLowerCase() // asegurarse que sea en minúscula
  });
  return response.data;
}

export async function submitLegislativeChoice(gameId, playerId, selectedIndex) {
  const response = await axios.post(`/games/${gameId}/legislative`, {
    playerId,
    selectedIndex,
  });
  return response.data;
}