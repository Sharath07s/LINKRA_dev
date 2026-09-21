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

/** Matches one EvidenceLink → DocumentChunk record from the backend */
export interface EvidenceLink {
  evidence_link_id: string;
  document_chunk_id: string;
  quote_snippet: string | null;
  char_start: number | null;
  char_end: number | null;
  confidence: number | null;
  chunk_index: number | null;
  page_number: number | null;
  source_filename: string | null;
}

/** Full response from GET /relationship/{id}/evidence */
export interface RelationshipEvidenceResponse {
  relationship_id: string;
  relationship_type: string;
  confidence: number | null;
  extraction_method: string | null;
  evidence_text: string | null;
  ingestion_job_id: string | null;
  source_page: number | null;
  source_row: number | null;
  source_filename: string | null;
  evidence_links: EvidenceLink[];
}

export const relationshipService = {
  async getEntityRelationships(entityId: string): Promise<EntityRelationship[]> {
    const response = await apiClient.get(`/relationship/entity/${entityId}`);
    return response.data.relationships;
  },

  async getRelationshipEvidence(relationshipId: string): Promise<RelationshipEvidenceResponse> {
    const response = await apiClient.get(`/relationship/${relationshipId}/evidence`);
    return response.data;
  },
};
