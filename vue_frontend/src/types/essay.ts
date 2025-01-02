export interface EssayHistory {
  id: number
  essay: string
  score: number | null
  error: string
  status: 'COMPLETED' | 'FAILED' | 'PENDING'
  created_at: string
}

export interface EssayHistoryResponse {
  count: number
  next: string | null
  previous: string | null
  results: EssayHistory[]
}
