import axios, { AxiosError } from 'axios';
import { apiClient } from '@/lib/api-client';

// Interfaces mapping to Backend Models
export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  message: string;
  provider: string;
  timestamp: string;
  status: string;
  intent?: string;
  structured_data?: Record<string, any>[] | null;
  record_count?: number;
}

export const chatService = {
  /**
   * Sends a message to the backend AI chat endpoint.
   * @param message The user's query text
   * @returns The ChatResponse from the AI
   */
  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>(
        `/chat/`,
        { query: message },
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
