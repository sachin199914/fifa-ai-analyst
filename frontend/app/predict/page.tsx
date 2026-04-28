'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'

interface PredictResponse {
  home_team: string
  away_team: string
  home_win_probability: number
  draw_probability: number
  away_win_probability: number
  prediction: string
  confidence: string
  home_stats: {
    played: number
    win_rate: string
    avg_goals_scored: number
    avg_goals_conceded: number
  }
  away_stats: {
    played: number
    win_rate: string
    avg_goals_scored: number
    avg_goals_conceded: number
  }
}

export default function PredictPage() {
  const [teams, setTeams] = useState<string[]>([])
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [result, setResult] = useState<PredictResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Load teams list on mount
  useEffect(() => {
    fetch('http://localhost:8000/teams')
      .then(r => r.json())
      .then(data => setTeams(data.teams))
      .catch(() => setError('Could not load teams list'))
  }, [])

  const predict = async () => {
    if (!homeTeam || !awayTeam) return
    if (homeTeam === awayTeam) {
      setError('Please select two different teams')
      return
    }
    setLoading(true)
    setResult(null)
    setError('')

    try {
      const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ home_team: homeTeam, away_team: awayTeam })
      })
      const data = await res.json()
      setResult(data)
    } catch {
      setError('Could not connect to backend.')
    } finally {
      setLoading(false)
    }
  }

  const confidenceColor = (c: string) => {
    if (c === 'High') return 'text-green-400'
    if (c === 'Medium') return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">

      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">⚽</span>
            <div>
              <h1 className="text-xl font-bold">FIFA World Cup AI Analyst</h1>
              <p className="text-gray-400 text-sm">Powered by RAG + Llama 3.1</p>
            </div>
          </div>
          {/* Nav */}
          <div className="flex gap-4 text-sm">
            <Link href="/" className="text-gray-400 hover:text-white transition-colors">Q&A</Link>
            <Link href="/predict" className="text-green-400 font-semibold border-b border-green-400">Predictor</Link>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-8">

        <h2 className="text-2xl font-bold mb-2">Match Outcome Predictor</h2>
        <p className="text-gray-400 mb-8 text-sm">
          Predict win probabilities based on historical performance data of 333 international teams
        </p>

        {/* Team Selection */}
        <div className="grid grid-cols-3 gap-4 mb-6 items-center">

          {/* Home Team */}
          <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <p className="text-xs text-gray-400 mb-2 font-semibold uppercase tracking-wide">Home Team</p>
            <select
              value={homeTeam}
              onChange={e => setHomeTeam(e.target.value)}
              className="w-full bg-transparent text-white outline-none text-sm"
            >
              <option value="" className="bg-gray-800">Select team...</option>
              {teams.map(t => (
                <option key={t} value={t} className="bg-gray-800">{t}</option>
              ))}
            </select>
          </div>

          {/* VS */}
          <div className="text-center">
            <p className="text-3xl font-bold text-gray-600">VS</p>
          </div>

          {/* Away Team */}
          <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <p className="text-xs text-gray-400 mb-2 font-semibold uppercase tracking-wide">Away Team</p>
            <select
              value={awayTeam}
              onChange={e => setAwayTeam(e.target.value)}
              className="w-full bg-transparent text-white outline-none text-sm"
            >
              <option value="" className="bg-gray-800">Select team...</option>
              {teams.map(t => (
                <option key={t} value={t} className="bg-gray-800">{t}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Predict Button */}
        <button
          onClick={predict}
          disabled={loading || !homeTeam || !awayTeam}
          className="w-full bg-green-600 hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed py-3 rounded-xl font-semibold transition-colors mb-6"
        >
          {loading ? 'Predicting...' : 'Predict Match Outcome'}
        </button>

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 text-red-300 text-sm mb-6">
            ⚠️ {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-4">

            {/* Prediction Banner */}
            <div className="bg-gray-800 rounded-xl p-6 border border-green-600 text-center">
              <p className="text-gray-400 text-sm mb-1">Predicted Outcome</p>
              <p className="text-3xl font-bold text-white mb-1">🏆 {result.prediction}</p>
              <p className={`text-sm font-semibold ${confidenceColor(result.confidence)}`}>
                {result.confidence} Confidence
              </p>
            </div>

            {/* Probability Bars */}
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <p className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wide">Win Probabilities</p>

              {/* Home Win */}
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span>{result.home_team}</span>
                  <span className="font-bold text-green-400">{result.home_win_probability}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-green-500 h-3 rounded-full transition-all duration-700"
                    style={{ width: `${result.home_win_probability}%` }}
                  />
                </div>
              </div>

              {/* Draw */}
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span>Draw</span>
                  <span className="font-bold text-yellow-400">{result.draw_probability}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-yellow-500 h-3 rounded-full transition-all duration-700"
                    style={{ width: `${result.draw_probability}%` }}
                  />
                </div>
              </div>

              {/* Away Win */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>{result.away_team}</span>
                  <span className="font-bold text-blue-400">{result.away_win_probability}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-blue-500 h-3 rounded-full transition-all duration-700"
                    style={{ width: `${result.away_win_probability}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Team Stats Comparison */}
            <div className="grid grid-cols-2 gap-4">
              {[
                { team: result.home_team, stats: result.home_stats, color: 'green' },
                { team: result.away_team, stats: result.away_stats, color: 'blue' }
              ].map(({ team, stats, color }) => (
                <div key={team} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
                  <p className={`text-sm font-bold mb-3 ${color === 'green' ? 'text-green-400' : 'text-blue-400'}`}>
                    {team}
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Matches Played</span>
                      <span className="font-semibold">{stats.played}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Win Rate</span>
                      <span className="font-semibold">{stats.win_rate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Avg Goals Scored</span>
                      <span className="font-semibold">{stats.avg_goals_scored}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Avg Goals Conceded</span>
                      <span className="font-semibold">{stats.avg_goals_conceded}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Reset */}
            <button
              onClick={() => { setResult(null); setHomeTeam(''); setAwayTeam('') }}
              className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              ← Try another match
            </button>
          </div>
        )}

        {/* Quick Match Suggestions */}
        {!result && !loading && (
          <div className="mt-6">
            <p className="text-gray-500 text-sm mb-3">Try these classic matchups:</p>
            <div className="flex flex-wrap gap-2">
              {[
                ['Brazil', 'Germany'],
                ['France', 'Argentina'],
                ['Spain', 'England'],
                ['Italy', 'Netherlands'],
              ].map(([home, away]) => (
                <button
                  key={`${home}-${away}`}
                  onClick={() => { setHomeTeam(home); setAwayTeam(away) }}
                  className="text-sm bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 px-3 py-2 rounded-lg transition-colors"
                >
                  {home} vs {away}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}