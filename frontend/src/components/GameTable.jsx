import React from 'react';
import Board from './Board';

import playerBase from '../assets/player-base.png';
import playerBaseUnselectable from '../assets/player-base-unselectable.png';
import iconLiberal from '../assets/player-icon-liberal.png';
import iconFascist from '../assets/player-icon-fascist.png';
import iconHitler from '../assets/player-icon-hitler.png';


export default function GameTable({ players = [], board }) {
  // División automática de jugadores
  const top = players.slice(0, 3);
  const left = players.slice(3, 5);
  const right = players.slice(5, 7);
  const bottom = players.slice(7);

  const renderPlayer = (player) => {
    const isPresident = board.government?.president?.id === player.id;
    const isChancellor = board.government?.chancellor?.id === player.id;

    const isDead = player.isAlive === false;
    const baseImg = isDead ? playerBaseUnselectable : playerBase;

    const roleVisible = player.role?.isVisible;
    const party = player.role?.party;

    let roleIcon = null;
    if (roleVisible) {
      if (party === 'Liberal') {
        roleIcon = iconLiberal;
      } else if (party === 'Fascist') {
        roleIcon = iconFascist;
      }
      if (player.role?.isHitler) {
        roleIcon = iconHitler;
      }
    }

    return (
      <div key={player.id} style={{ position: 'relative', width: '80px' }}>
        <img src={baseImg} alt="Jugador" style={{ width: '100%' }} />

        {/* Nombre */}
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

        {/* Íconos de estado */}
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

        {/* Icono de rol */}
        {roleVisible && roleIcon && (
          <img
            src={roleIcon}
            alt="Partido"
            style={{
              position: 'absolute',
              top: '-18px',
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
      {/* Top */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
        {top.map(renderPlayer)}
      </div>

      {/* Center (left - board - right) */}
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '2rem' }}>
        {/* Left */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {left.map(renderPlayer)}
        </div>

        {/* Board */}
        <Board
          liberalPolicies={board.liberalPolicies}
          fascistPolicies={board.fascistPolicies}
          policiesInDeck={board.policiesInDeck}
          policiesInDiscard={board.policiesInDiscard}
        />

        {/* Right */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {right.map(renderPlayer)}
        </div>
      </div>

      {/* Bottom */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
        {bottom.map(renderPlayer)}
      </div>
    </div>
  );
}