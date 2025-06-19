// src/api/gameApi.jsAdd commentMore actions
import axios from 'axios';

const API_BASE = 'http://localhost:5000';  // Ajusta según tu entorno

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

export async function getGameState(gameId, playerId) {
  const url = `${API_BASE}/games/${gameId}/state?playerId=${playerId}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Error al obtener el estado");
  return await res.json();
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

export async function triggerNomination(gameId, chancellorId = null) {
  const response = await axios.post(
    `http://127.0.0.1:5000/games/${gameId}/nominate`,
    chancellorId !== null ? { nomineeId: chancellorId } : {}
  );
  return response.data;
}



export async function submitVote(gameId, playerId, vote) {
    console.log("🗳️ Enviando voto:", { gameId, playerId, vote });
  const response = await axios.post(`${API_BASE}/games/${gameId}/vote`, {
    playerId: playerId,
    vote: vote.toLowerCase() // asegurarse que sea en minúscula
  });
  console.log("✅ Respuesta del servidor:", response.data);
  return response.data;
}

export async function drawLegislativeCards(gameId) {
  const response = await axios.post(`${API_BASE}/games/${gameId}/president/draw`, {
  });
  return response.data;
}

export async function discardLegislativeCard(gameId, discardIndex) {
  const response = await axios.post(`${API_BASE}/games/${gameId}/president/discard`, {
    discardIndex: discardIndex
  });
  return response.data;
}

export async function encactChancellorPolicy(gameId, enactIndex) {
  const response = await axios.post(`${API_BASE}/games/${gameId}/chancellor/enact`, {
    enactIndex: enactIndex
  });
  return response.data;
}


export async function submitExecution(gameId, powerType, targetPlayerId) {
  console.log("👉 Enviando ejecución:", { powerType });
  const response = await axios.post(`${API_BASE}/games/${gameId}/executive/execute`, {
    powerType: powerType,
    targetPlayerId: targetPlayerId
  });
  return response.data;
}