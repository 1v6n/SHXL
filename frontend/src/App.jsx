
import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Game from './pages/Game'
import Match from './pages/Match';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/game/:gameId" element={<Game />} />
      <Route path="/match/:gameId" element={<Match />} />
    </Routes>
  )
}