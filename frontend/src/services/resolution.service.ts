import { apiClient } from '@/lib/api-client';

export interface PossibleMatch {
  canonical_entity_id: string;
  name: string;
  match_score: number;
}

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
  possible_matches: PossibleMatch[];
}

export const ResolutionService = {
  getReviewQueue: async (skip: number = 0, limit: number = 50): Promise<ResolutionReviewResponse[]> => {
    const response = await apiClient.get('/resolution/review-queue', { params: { skip, limit } });
    return response.data;
  },
  confirmMatch: async (candidateId: string, canonicalEntityId: string): Promise<void> => {
    await apiClient.post(`/resolution/${candidateId}/confirm`, {
      canonical_entity_id: canonicalEntityId
    });
  },
  createNewEntity: async (candidateId: string, name: string): Promise<void> => {
    await apiClient.post(`/resolution/${candidateId}/create-entity`, {
      name: name
    });
  },
  rejectMatch: async (candidateId: string): Promise<void> => {
    await apiClient.post(`/resolution/${candidateId}/reject`);
  }
};
