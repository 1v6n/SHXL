import React from 'react';
import Board from './Board';

import playerBase from '../assets/player-base.png';
import playerBaseUnselectable from '../assets/player-base-unselectable.png';
import iconLiberal from '../assets/player-icon-liberal.png';
import iconFascist from '../assets/player-icon-fascist.png';
import iconHitler from '../assets/player-icon-hitler.png';

export default function GameTable({ players = [], board, government, playerId }) {
  const thisPlayer = players.find(p => String(p.id) === String(playerId));
  const isFascist = thisPlayer?.role?.party === 'fascist' && !thisPlayer?.role?.isHitler;
  const totalPlayers = players.length;

  const top = players.slice(0, 3);
  const left = players.slice(3, 5);
  const right = players.slice(5, 7);
  const bottom = players.slice(7);

  const renderPlayer = (player) => {
    const isPresident = String(government?.president?.id) === String(player.id);
    const isChancellor = 
      String(government?.chancellor?.id) === String(player.id) ||
      String(government?.chancellorCandidate?.id) === String(player.id);
    const isDead = player.isAlive === false;
    const baseImg = isDead ? playerBaseUnselectable : playerBase;

    const party = player.role?.party;
    const isHitler = player.role?.isHitler;

    const roleVisible =
      player.id === playerId || // Siempre ves tu propio rol
      (isFascist && isHitler && totalPlayers <= 6); // Fascistas ven a Hitler en partidas 5-6

    let roleIcon = null;
    if (roleVisible) {
      if (party === 'liberal') roleIcon = iconLiberal;
      else if (party === 'fascist') roleIcon = iconFascist;
      if (isHitler) roleIcon = iconHitler;
    }

    return (
      <div key={player.id} style={{ position: 'relative', width: '80px' }}>
        <img src={baseImg} alt="Jugador" style={{ width: '100%' }} />

        <div
          style={{
            position: 'absolute',
            top: '8px',
            width: '100%',
            textAlign: 'center',
            fontSize: '0.7rem',
          }}
        >
          <strong>{player.name}</strong>
        </div>

        <div
          style={{
            position: 'absolute',
            bottom: '8px',
            width: '100%',
            textAlign: 'center',
            fontSize: '1rem',
          }}
        >
          {isDead && '💀'}
          {player.isBot && '🤖'}
          {isPresident && '⭐'}
          {isChancellor && '🎯'}
        </div>

        {roleVisible && roleIcon && (
          <img
            src={roleIcon}
            alt="Partido"
            style={{
              position: 'absolute',
              top: '-22px',
              left: '50%',
              transform: 'translateX(-50%)',
              height: '30px',
              opacity: isDead ? 0.3 : 1,
            }}
          />
        )}
      </div>
    );
  };

  return (
    <div style={{ display: 'grid', gridTemplateRows: 'auto 1fr auto', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
        {top.map(renderPlayer)}
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '2rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {left.map(renderPlayer)}
        </div>

        <Board
          liberalPolicies={board.liberalPolicies}
          fascistPolicies={board.fascistPolicies}
          policiesInDeck={board.policiesInDeck}
          policiesInDiscard={board.policiesInDiscard}
          failedElections={board.failedElections}
        />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {right.map(renderPlayer)}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
        {bottom.map(renderPlayer)}
      </div>
    </div>
  );
}
