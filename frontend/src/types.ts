export type AgentName = 'planner' | 'researcher' | 'analyst' | 'writer' | 'system'

export interface AgentEvent {
  type: 'agent_start' | 'agent_update' | 'complete' | 'error'
  agent?: AgentName
  status?: 'running' | 'done' | 'error'
  message: string
  data?: {
    sub_questions?: string[]
    sources?: string[]
    sources_found?: number
  } | null
  report?: string
  session_id?: string
}

export interface ResearchSession {
  id: string
  task: string
  status: string
  created_at: string
}
