'use client'
import { useState } from 'react'

const SAMPLE_QUESTIONS = [
  "Who won the 2014 FIFA World Cup?",
  "How many World Cups has Brazil won?",
  "Compare France and Germany's World Cup records",
  "Which country hosted the 2006 World Cup?",
  "Who won the 2022 World Cup final?"
]

export default function Home() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const askQuestion = async () => {
    if (!question.trim()) return
    setLoading(true)
    setAnswer('')
    setSources([])
    setError('')

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, n_results: 5 })
      })

      if (!res.ok) throw new Error('API error')

      const data = await res.json()
      setAnswer(data.answer)
      setSources(data.sources)
    } catch (err) {
      setError('Could not connect to backend. Make sure it is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <span className="text-3xl">⚽</span>
          <div>
            <h1 className="text-xl font-bold">FIFA World Cup AI Analyst</h1>
            <p className="text-gray-400 text-sm">Powered by RAG + Llama 3.1</p>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-8">

        {/* Search Box */}
        <div className="mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !loading && askQuestion()}
              placeholder="Ask anything about FIFA World Cup history..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition-colors placeholder-gray-500"
            />
            <button
              onClick={askQuestion}
              disabled={loading || !question.trim()}
              className="bg-green-600 hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed px-6 py-3 rounded-xl font-semibold transition-colors whitespace-nowrap"
            >
              {loading ? 'Thinking...' : 'Ask AI'}
            </button>
          </div>
        </div>

        {/* Sample Questions */}
        {!answer && !loading && (
          <div className="mb-8">
            <p className="text-gray-500 text-sm mb-3">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_QUESTIONS.map(q => (
                <button
                  key={q}
                  onClick={() => setQuestion(q)}
                  className="text-sm bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-green-600 text-gray-300 px-3 py-2 rounded-lg transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 animate-pulse">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay:'0.1s'}}></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay:'0.2s'}}></div>
              <span className="text-gray-400 text-sm ml-1">Searching World Cup data...</span>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 text-red-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Answer */}
        {answer && (
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-green-400 text-sm font-semibold">🤖 AI ANSWER</span>
              </div>
              <p className="text-gray-100 leading-relaxed">{answer}</p>
            </div>

            {/* Sources */}
            {sources.length > 0 && (
              <div>
                <p className="text-gray-500 text-xs mb-2">Sources used:</p>
                <div className="flex flex-wrap gap-2">
                  {sources.map((s, i) => (
                    <span
                      key={i}
                      className="text-xs bg-gray-800 border border-gray-700 text-gray-400 px-2 py-1 rounded-md"
                    >
                      {s.type === 'match' ? `⚽ ${s.home_team} vs ${s.away_team} (${s.year})` : 
                       s.type === 'tournament' ? `🏆 ${s.year} World Cup` :
                       `📊 ${s.team}`}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Ask another */}
            <button
              onClick={() => { setAnswer(''); setQuestion(''); setSources([]) }}
              className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              ← Ask another question
            </button>
          </div>
        )}
      </div>
    </main>
  )
}