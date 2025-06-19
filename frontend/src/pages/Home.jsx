import './Home.css';
import bg from '../assets/lobby-bg.png';
import JoinLobby from '../components/JoinLobby';
import CreateLobby from '../components/CreateLobby';
import { createGame, joinGame } from '../api/gameApi.js';

export default function Home() {
  const handleCreate = async ({ playerName }) => {
    const game = await createGame({ playerName });
    // redirigir a: /game/:game.id
    console.log('Created', game);
  };

  const handleJoin = async ({ lobbyCode, playerName }) => {
    const game = await joinGame(lobbyCode, playerName);
    console.log('Joined', game);
  };

  return (
    <div
      className="home-container"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="forms-wrapper">
        <JoinLobby onJoin={handleJoin} />
        <CreateLobby onCreate={handleCreate} />
      </div>
    </div>
  );
}