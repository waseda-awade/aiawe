import api from '@/services/api'

export interface EssayRequest {
  id: number
  essay: string
  result: string | number | null
  error: string | null
  status: 'PENDING' | 'COMPLETED' | 'FAILED'
  created_at: string
}

export interface EssayListResponse {
  count: number
  next: string | null
  previous: string | null
  results: EssayRequest[]
}

export class EssayService {
  public static async submitEssay(essay: string): Promise<EssayRequest> {
    const response = await api.post<EssayRequest>('/requests/', { essay })
    return response.data
  }

  public static async getEssay(requestId: number): Promise<EssayRequest> {
    const response = await api.get<EssayRequest>(`/requests/${requestId}/`)
    return response.data
  }

  public static async getEssayHistory(
    page: number = 1,
    pageSize: number = 10,
  ): Promise<EssayListResponse> {
    const response = await api.get<EssayListResponse>('/requests/', {
      params: { page, page_size: pageSize },
    })
    return response.data
  }
}
