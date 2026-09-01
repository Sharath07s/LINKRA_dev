import { apiClient } from '@/lib/api-client';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authService = {
  /**
   * Logs in a user using badge number and password
   * @param badge_number 
   * @param password 
   * @returns 
   */
  async login(badge_number: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', badge_number);
    formData.append('password', password);

    const response = await apiClient.post<LoginResponse>(
      `/auth/login`,
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    return response.data;
  }
};
