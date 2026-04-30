import { useEffect, useRef } from 'react'
import { Brain, Globe, BarChart2, FileText, CheckCircle2, Loader2, AlertCircle, Info, Zap } from 'lucide-react'
import type { AgentEvent, AgentName } from '../types'

const AGENT_CONFIG: Record<AgentName, { label: string; icon: React.ReactNode; color: string }> = {
  planner:    { label: 'Planner',    icon: <Brain className="w-4 h-4" />,      color: 'text-blue-400' },
  researcher: { label: 'Researcher', icon: <Globe className="w-4 h-4" />,      color: 'text-green-400' },
  analyst:    { label: 'Analyst',    icon: <BarChart2 className="w-4 h-4" />,  color: 'text-yellow-400' },
  writer:     { label: 'Writer',     icon: <FileText className="w-4 h-4" />,   color: 'text-violet-400' },
  system:     { label: 'System',     icon: <Zap className="w-4 h-4" />,        color: 'text-zinc-400' },
}

interface Props {
  events: AgentEvent[]
  isLoading: boolean
  error: string | null
}

export default function AgentTimeline({ events, isLoading, error }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events])

  if (events.length === 0 && !isLoading && !error) return null

  return (
    <div className="w-full max-w-3xl mx-auto mt-8">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800 bg-zinc-950">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/70" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
            <div className="w-3 h-3 rounded-full bg-green-500/70" />
          </div>
          <span className="text-zinc-500 text-xs font-mono ml-2">agent.log</span>
          {isLoading && (
            <div className="ml-auto flex items-center gap-1.5 text-violet-400 text-xs">
              <Loader2 className="w-3 h-3 animate-spin" />
              running
            </div>
          )}
        </div>

        <div className="p-4 space-y-2 max-h-72 overflow-y-auto font-mono text-sm">
          {events.map((event, i) => {
            const agentKey = event.agent as AgentName
            const config = agentKey ? AGENT_CONFIG[agentKey] : null

            if (event.type === 'agent_start') {
              return (
                <div key={i} className="flex items-start gap-3 text-zinc-400">
                  <span className="text-zinc-600 text-xs mt-0.5 shrink-0">›</span>
                  {config && (
                    <span className={`${config.color} shrink-0 mt-0.5`}>{config.icon}</span>
                  )}
                  <span>{event.message}</span>
                </div>
              )
            }

            if (event.type === 'agent_update') {
              const isDone = event.status === 'done'
              const isWarning = event.status === 'warning'
              const isSystem = agentKey === 'system'
              return (
                <div key={i} className="flex items-start gap-3">
                  {isWarning ? (
                    <AlertCircle className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5" />
                  ) : isSystem ? (
                    <Info className="w-4 h-4 text-zinc-500 shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
                  )}
                  {config && !isSystem && (
                    <span className={`text-xs ${config.color} font-semibold shrink-0 mt-0.5 w-20`}>
                      [{config.label}]
                    </span>
                  )}
                  <span className={isWarning ? 'text-yellow-400' : isSystem ? 'text-zinc-500 italic' : 'text-zinc-300'}>
                    {event.message}
                  </span>
                  {event.data?.sources_found !== undefined && (
                    <span className="text-zinc-600 text-xs ml-auto shrink-0">
                      {event.data.sources_found} sources
                    </span>
                  )}
                </div>
              )
            }
          })}

          {error && (
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {isLoading && (
            <div className="flex items-center gap-2 text-zinc-600">
              <span className="animate-pulse">▋</span>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  )
}
