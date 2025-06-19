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