import { apiClient } from "@/lib/api-client";

export interface Investigation {
  id: string;
  crime_id: string;
  priority: string;
  status: string;
  started_at: string;
}

export const investigationService = {
  listInvestigations: async (): Promise<Investigation[]> => {
    const response = await apiClient.get('/investigations/');
    return response.data;
  },
  
  getInvestigation: async (id: string): Promise<Investigation> => {
    const response = await apiClient.get(`/investigations/${id}`);
    return response.data;
  }
};
