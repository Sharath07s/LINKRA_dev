/**
 * Ingestion API service.
 * Communicates with the LINKRA backend ingestion endpoints.
 */
import { apiClient } from '@/lib/api-client';

// ── Types ──────────────────────────────────────────────────────────────

export interface EntityCandidate {
  id: string;
  entity_type: string;
  raw_text: string;
  normalized_value: string | null;
  confidence: number | null;
  source_page: number | null;
  source_row: number | null;
  start_offset: number | null;
  end_offset: number | null;
  extraction_method: string;
  created_at: string;
}

export interface IngestionJob {
  id: string;
  file_name: string;
  source_type: string;
  file_type: string;
  file_size_bytes: number | null;
  status: string;
  error_message: string | null;
  record_count: number | null;
  entity_count: number | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface IngestionJobDetail extends IngestionJob {
  entities: EntityCandidate[];
}

export const SOURCE_TYPES = [
  { value: "FIR", label: "First Information Report (FIR)" },
  { value: "POLICE_REPORT", label: "Police Report" },
  { value: "CDR", label: "Call Detail Record (CDR)" },
  { value: "FINANCIAL_TRANSACTION", label: "Financial Transaction" },
  { value: "SURVEILLANCE_REPORT", label: "Surveillance Report" },
  { value: "SOCIAL_MEDIA", label: "Social Media Intelligence" },
  { value: "CRIMINAL_HISTORY", label: "Criminal History" },
  { value: "INTELLIGENCE_REPORT", label: "Intelligence Report" },
  { value: "OTHER", label: "Other" },
];

// ── API Functions ──────────────────────────────────────────────────────

export const ingestionService = {
  /**
   * Upload a file for ingestion.
   */
  async uploadFile(file: File, sourceType: string): Promise<IngestionJob> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_type", sourceType);

    const response = await apiClient.post<IngestionJob>(
      "/ingestion/upload",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000, // 2 minutes for large files
      }
    );
    return response.data;
  },

  /**
   * List all ingestion jobs.
   */
  async listJobs(): Promise<IngestionJob[]> {
    const response = await apiClient.get<IngestionJob[]>("/ingestion/");
    return response.data;
  },

  /**
   * Get detailed information about an ingestion job, including entities.
   */
  async getJobDetail(jobId: string): Promise<IngestionJobDetail> {
    const response = await apiClient.get<IngestionJobDetail>(`/ingestion/${jobId}`);
    return response.data;
  },

  /**
   * Get extracted entity candidates for a job, optionally filtered by type.
   */
  async getJobEntities(jobId: string, entityType?: string): Promise<EntityCandidate[]> {
    const params = entityType ? { entity_type: entityType } : {};
    const response = await apiClient.get<EntityCandidate[]>(
      `/ingestion/${jobId}/entities`,
      { params }
    );
    return response.data;
  },
};
