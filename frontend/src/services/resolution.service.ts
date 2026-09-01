import { apiClient } from '@/lib/api-client';

export interface ResolutionReviewResponse {
  candidate_id: string;
  entity_type: string;
  raw_text: string;
  normalized_value: string;
  confidence: number | null;
  source_info: string;
  proposed_canonical_id: string | null;
  proposed_canonical_name: string | null;
  resolution_score: number | null;
}

export const ResolutionService = {
  getReviewQueue: async (skip: number = 0, limit: number = 50): Promise<ResolutionReviewResponse[]> => {
    const response = await apiClient.get('/resolution/review-queue', { params: { skip, limit } });
    return response.data;
  },
  approveMatch: async (candidateId: string): Promise<void> => {
    await apiClient.post(`/resolution/${candidateId}/approve`);
  },
  createNewEntity: async (candidateId: string): Promise<void> => {
    await apiClient.post(`/resolution/${candidateId}/create-entity`);
  }
};
