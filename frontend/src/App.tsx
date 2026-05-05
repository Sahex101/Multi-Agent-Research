import { useEffect, useState } from 'react'
import ResearchForm from './components/ResearchForm'
import AgentTimeline from './components/AgentTimeline'
import ReportViewer from './components/ReportViewer'
import { useResearch } from './hooks/useResearch'
import type { ResearchSession } from './types'
import { History, X } from 'lucide-react'

const apiBase = (typeof __API_URL__ !== 'undefined' && __API_URL__) ? __API_URL__ : ''

export default function App() {
  const { events, report, isLoading, error, sessionId, startResearch, reset } = useResearch()
  const [sessions, setSessions] = useState<ResearchSession[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [historyReport, setHistoryReport] = useState<string | null>(null)
  const [historySessionId, setHistorySessionId] = useState<string | null>(null)

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${apiBase}/api/sessions`)
      if (res.ok) setSessions(await res.json())
    } catch {
      // backend may not be running
    }
  }

  useEffect(() => {
    fetchSessions()
  }, [report]) // refetch after each completed research

  const loadSession = async (id: string) => {
    try {
      const res = await fetch(`${apiBase}/api/sessions/${id}`)
      if (res.ok) {
        const data = await res.json()
        if (data.final_report) {
          setHistoryReport(data.final_report)
          setHistorySessionId(data.id)
        }
        setShowHistory(false)
      }
    } catch {}
  }

  const handleReset = () => {
    reset()
    setHistoryReport(null)
    setHistorySessionId(null)
  }

  const displayReport = report ?? historyReport
  const displaySessionId = sessionId ?? historySessionId

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Subtle grid background */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-30 pointer-events-none" />

      {/* Header */}
      <header className="relative z-10 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur sticky top-0">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-zinc-400 text-xs font-mono">
            <span className="text-violet-400 font-bold">SA.</span>
            <span className="text-zinc-700">/</span>
            <span>multi-agent-research</span>
          </div>
          <button
            onClick={() => { setShowHistory(!showHistory); fetchSessions() }}
            className="flex items-center gap-1.5 text-zinc-500 hover:text-zinc-300 text-xs transition-colors"
          >
            <History className="w-3.5 h-3.5" />
            History
          </button>
        </div>
      </header>

      {/* History panel */}
      {showHistory && (
        <div className="fixed right-0 top-12 h-full w-80 bg-zinc-900 border-l border-zinc-800 z-20 overflow-y-auto">
          <div className="flex items-center justify-between p-4 border-b border-zinc-800">
            <span className="text-zinc-300 text-sm font-semibold">Research History</span>
            <button onClick={() => setShowHistory(false)}>
              <X className="w-4 h-4 text-zinc-500 hover:text-zinc-300" />
            </button>
          </div>
          <div className="p-3 space-y-2">
            {sessions.length === 0 && (
              <p className="text-zinc-600 text-xs p-2">No sessions yet.</p>
            )}
            {sessions.map(s => (
              <button
                key={s.id}
                onClick={() => loadSession(s.id)}
                className="w-full text-left p-3 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition-colors"
              >
                <p className="text-zinc-200 text-xs line-clamp-2">{s.task}</p>
                <div className="flex items-center justify-between mt-1.5">
                  <span className={`text-xs ${s.status === 'done' ? 'text-green-400' : s.status === 'error' ? 'text-red-400' : 'text-yellow-400'}`}>
                    {s.status}
                  </span>
                  <span className="text-zinc-600 text-xs">
                    {new Date(s.created_at).toLocaleDateString()}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="relative z-10 max-w-5xl mx-auto px-4 py-12">
        <ResearchForm
          onSubmit={startResearch}
          isLoading={isLoading}
          onReset={handleReset}
        />

        <AgentTimeline
          events={events}
          isLoading={isLoading}
          error={error}
        />

        {displayReport && (
          <ReportViewer report={displayReport} sessionId={displaySessionId} />
        )}
      </main>
    </div>
  )
}
