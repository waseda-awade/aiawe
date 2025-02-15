import api from '@/services/api'
import type { EssayRequest, EssayListResponse } from '@/types/essay'

export class EssayService {
  public static async submitEssay({
    essay,
    essay_topic,
    model_id
  }: {
    essay: string,
    essay_topic: string,
    model_id: number
  }): Promise<EssayRequest> {
    const response = await api.post<EssayRequest>('/requests/', {
      essay,
      essay_topic,
      model_id
    })
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

  public static async deleteEssays(ids: number[]): Promise<void> {
    await api.post('/requests/bulk_delete/', { ids })
  }
}
