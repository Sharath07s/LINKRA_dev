import { apiClient } from '@/lib/api-client';

export interface EntityRelationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relationship_type: string;
  confidence: number;
  extraction_method: string;
  event_timestamp: string | null;
  ingestion_job_id: string;
  source_page: number | null;
  source_row: number | null;
}

export const relationshipService = {
  async getEntityRelationships(entityId: string): Promise<EntityRelationship[]> {
    const response = await apiClient.get(`/relationship/entity/${entityId}`);
    return response.data.relationships;
  },
};
