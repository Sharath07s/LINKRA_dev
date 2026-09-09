export interface PointGeometry {
  type: "Point";
  coordinates: [number, number]; // [longitude, latitude]
}

export interface CrimeProperties {
  crime_id: string;
  fir_number: string | null;
  crime_type: string | null;
  district: string | null;
  station: string | null;
  occurrence_date: string | null;
  status: string | null;
  estimated_loss: number | null;
  title: string | null;
}

export interface StationProperties {
  station_id: string;
  station_code: string;
  station_name: string;
  district: string | null;
  address: string | null;
}

export interface GeoJSONFeature<T> {
  type: "Feature";
  geometry: PointGeometry;
  properties: T;
}

export interface GeoJSONFeatureCollection<T> {
  type: "FeatureCollection";
  features: GeoJSONFeature<T>[];
}

export type CrimeFeatureCollection = GeoJSONFeatureCollection<CrimeProperties>;
export type StationFeatureCollection = GeoJSONFeatureCollection<StationProperties>;

export interface PolygonGeometry {
  type: "Polygon";
  coordinates: number[][][]; // [[[lon, lat], ...]]
}

export interface DensityProperties {
  cluster_id: number;
  crime_count: number;
  density_score: number;
}

export interface DensityFeature {
  type: "Feature";
  geometry: PolygonGeometry;
  properties: DensityProperties;
}

export interface DensityFeatureCollection {
  type: "FeatureCollection";
  features: DensityFeature[];
}

export interface CrimeMapFilters {
  district_id?: string;
  crime_type_id?: string;
  investigation_id?: string;
  start_date?: string;
  end_date?: string;
}

export interface FilterOption {
  id: string;
  name: string;
}

export interface FilterOptionsResponse {
  districts: FilterOption[];
  crime_types: FilterOption[];
  investigations: FilterOption[];
}
