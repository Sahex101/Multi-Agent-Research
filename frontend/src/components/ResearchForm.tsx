import { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'

interface Props {
  onSubmit: (task: string, maxQueries: number) => void
  isLoading: boolean
  onReset: () => void
}

const EXAMPLE_TASKS = [
  'What are the latest breakthroughs in LLM reasoning and chain-of-thought prompting?',
  'How is AI being used in healthcare diagnostics in 2024-2025?',
  'What are the best practices for building production-ready RAG systems?',
  'Compare the top vector databases: Pinecone, Weaviate, and Qdrant',
]

export default function ResearchForm({ onSubmit, isLoading, onReset }: Props) {
  const [task, setTask] = useState('')
  const [maxQueries, setMaxQueries] = useState(3)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (task.trim()) onSubmit(task.trim(), maxQueries)
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="mb-8 text-center">
        <div className="inline-flex items-center gap-2 text-violet-400 text-sm font-mono mb-3 tracking-wider uppercase">
          <span className="w-8 h-px bg-violet-500" />
          Multi-Agent Research
          <span className="w-8 h-px bg-violet-500" />
        </div>
        <h1 className="text-4xl font-bold text-white mb-2">
          Research <span className="text-violet-400">Assistant</span>
        </h1>
        <p className="text-zinc-400 text-sm">
          Planner → Researcher → Analyst → Writer — powered by free LLMs
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            value={task}
            onChange={e => setTask(e.target.value)}
            placeholder="What do you want to research? Be specific for better results..."
            rows={3}
            disabled={isLoading}
            className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 resize-none transition-colors disabled:opacity-50"
          />
        </div>

        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <label className="text-zinc-400 text-sm whitespace-nowrap">Search depth:</label>
            <div className="flex gap-1">
              {[2, 3, 4].map(n => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setMaxQueries(n)}
                  disabled={isLoading}
                  className={`px-3 py-1 rounded-lg text-sm font-mono transition-colors ${
                    maxQueries === n
                      ? 'bg-violet-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  } disabled:opacity-50`}
                >
                  {n}
                </button>
              ))}
            </div>
            <span className="text-zinc-600 text-xs">sub-questions</span>
          </div>

          <div className="flex gap-2">
            {isLoading && (
              <button
                type="button"
                onClick={onReset}
                className="px-4 py-2 rounded-xl bg-zinc-800 text-zinc-300 hover:bg-zinc-700 text-sm transition-colors"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={isLoading || !task.trim()}
              className="flex items-center gap-2 px-6 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Researching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Research
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Example prompts */}
      {!isLoading && (
        <div className="mt-6">
          <p className="text-zinc-600 text-xs mb-2">Try an example:</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_TASKS.map(ex => (
              <button
                key={ex}
                onClick={() => setTask(ex)}
                className="text-xs bg-zinc-900 border border-zinc-700 hover:border-violet-600 text-zinc-400 hover:text-zinc-200 px-3 py-1.5 rounded-lg transition-colors text-left"
              >
                {ex.length > 60 ? ex.slice(0, 60) + '…' : ex}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
