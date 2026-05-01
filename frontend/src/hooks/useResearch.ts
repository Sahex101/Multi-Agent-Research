import { useState, useRef, useCallback } from 'react'
import type { AgentEvent } from '../types'

interface UseResearchReturn {
  events: AgentEvent[]
  report: string | null
  isLoading: boolean
  error: string | null
  sessionId: string | null
  startResearch: (task: string, maxQueries: number) => void
  reset: () => void
}

export function useResearch(): UseResearchReturn {
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [report, setReport] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const reset = useCallback(() => {
    abortRef.current?.abort()
    setEvents([])
    setReport(null)
    setIsLoading(false)
    setError(null)
    setSessionId(null)
  }, [])

  const startResearch = useCallback(async (task: string, maxQueries: number) => {
    reset()
    setIsLoading(true)
    const controller = new AbortController()
    abortRef.current = controller

    // In production VITE_API_URL points to Heroku backend; in dev proxy handles /api
    const apiBase = (typeof __API_URL__ !== 'undefined' && __API_URL__) ? __API_URL__ : ''

    try {
      const response = await fetch(`${apiBase}/api/research/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, max_search_queries: maxQueries }),
        signal: controller.signal,
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      if (!response.body) throw new Error('No response body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event: AgentEvent = JSON.parse(line.slice(6))
            if (event.type === 'complete') {
              setReport(event.report ?? null)
              setSessionId(event.session_id ?? null)
              setIsLoading(false)
            } else if (event.type === 'error') {
              setError(event.message)
              setIsLoading(false)
            } else {
              setEvents(prev => [...prev, event])
            }
          } catch {
            // skip malformed lines
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setError(err.message)
      }
      setIsLoading(false)
    }
  }, [reset])

  return { events, report, isLoading, error, sessionId, startResearch, reset }
}
