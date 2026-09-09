import { apiClient } from "@/lib/api-client";
import { CrimeFeatureCollection, StationFeatureCollection, CrimeMapFilters, FilterOptionsResponse, DensityFeatureCollection } from "@/types/geo.types";

export const geoService = {
  /**
   * Fetch filter options for the map.
   */
  async getFilterOptions(): Promise<FilterOptionsResponse> {
    const response = await apiClient.get<FilterOptionsResponse>("/geo/filter-options");
    return response.data;
  },

  /**
   * Fetch crime locations.
   */
  async getCrimeLocations(filters?: CrimeMapFilters & { bbox?: string, limit?: number }): Promise<CrimeFeatureCollection> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get<CrimeFeatureCollection>("/geo/crimes", { params });
    return response.data;
  },

  /**
   * Fetch police station locations.
   */
  async getStationLocations(bbox?: string, limit?: number): Promise<StationFeatureCollection> {
    const params = new URLSearchParams();
    if (bbox) params.append("bbox", bbox);
    if (limit) params.append("limit", limit.toString());
    
    const response = await apiClient.get<StationFeatureCollection>("/geo/stations", { params });
    return response.data;
  },

  /**
   * Fetch algorithmic crime density / spatial hotspots.
   */
  async getCrimeDensity(filters?: CrimeMapFilters & { bbox?: string }): Promise<DensityFeatureCollection> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const response = await apiClient.get<DensityFeatureCollection>("/geo/crime-density", { params });
    return response.data;
  }
};
