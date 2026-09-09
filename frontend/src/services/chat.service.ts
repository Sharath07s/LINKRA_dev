import axios, { AxiosError } from 'axios';
import { apiClient } from '@/lib/api-client';

export interface CopilotQuery {
  message: string;
  investigation_id?: string;
  entity_id?: string;
  conversation_id?: string;
}

export interface CopilotCitation {
  type: string;
  id: string;
  label: string;
  context?: string;
}

export interface CopilotResponse {
  status: string;
  answer: string;
  intent?: string;
  sources: CopilotCitation[];
  evidence: Record<string, any>[];
  entities: Record<string, any>[];
  analytics: Record<string, any>[];
  warnings: string[];
  provider?: string;
  grounded: boolean;
}

export const chatService = {
  /**
   * Sends a message to the backend AI chat endpoint.
   * @param message The user's query text
   * @returns The CopilotResponse from the AI
   */
  async sendMessage(message: string): Promise<CopilotResponse> {
    try {
      const payload: CopilotQuery = { message };
      const response = await apiClient.post<CopilotResponse>(
        `/copilot/chat`,
        payload,
        {
          timeout: 60000,
        }
      );
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        if (axiosError.response) {
          console.warn('Chat API Error Data:', axiosError.response.data);
          
          if (axiosError.response.status === 401 || axiosError.response.status === 403) {
             throw new Error("Authentication failed. Please log in again.");
          }
          if (axiosError.response.status === 429) {
             throw new Error("Too many requests. Please try again later.");
          }
          if (axiosError.response.status >= 500) {
             throw new Error("Backend server encountered an error processing the AI response.");
          }
        } else if (axiosError.request) {
          console.warn('Chat API Network/Timeout Error:', axiosError.request);
          throw new Error("Network error or timeout. The AI service took too long to respond.");
        }
      }
      throw new Error("An unexpected error occurred while communicating with the assistant.");
    }
  }
};
