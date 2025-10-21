import { useState, useEffect } from 'react'
import './App.css'
import WeatherDashboard from './components/WeatherDashboard'

function App() {
  return (
    <>
      <div className="app">
        <header className="app-header">
          <h1>Ethiopian Weather Dashboard</h1>
          <p>Three-Day Weather Forecast for Major Ethiopian Cities</p>
        </header>
        <main>
          <WeatherDashboard />
        </main>
      </div>
    </>
  )
}

export default App