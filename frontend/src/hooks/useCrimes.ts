import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../store/authStore';
import { apiClient } from "@/lib/api-client";

export const useCrimes = () => {
  const token = useAuthStore((state) => state.token);

  return useQuery({
    queryKey: ['crimes'],
    queryFn: async () => {
      const res = await apiClient.get(`/crimes`);
      return res.data;
    },
    enabled: !!token,
  });
};
