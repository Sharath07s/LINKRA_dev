"use client";

import { useState, useEffect, useCallback } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { 
  Layers, MapPin, Calendar, Sliders, ShieldAlert, Loader2, MapIcon, Activity
} from "lucide-react";
import Map, { Source, Layer } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import { geoService } from "@/services/geo.service";
import { FilterOptionsResponse, CrimeMapFilters, CrimeProperties, DensityFeatureCollection } from "@/types/geo.types";

export default function CrimeMapPage() {
  const [filterOptions, setFilterOptions] = useState<FilterOptionsResponse | null>(null);
  
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [selectedCrime, setSelectedCrime] = useState("");
  const [selectedInvestigation, setSelectedInvestigation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  
  const [geoData, setGeoData] = useState<any>(null);
  const [densityData, setDensityData] = useState<DensityFeatureCollection | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCrime, setActiveCrime] = useState<CrimeProperties | null>(null);
  const [activeCluster, setActiveCluster] = useState<{ cluster_id: number; crime_count: number; density_score: number } | null>(null);
  
  const [bbox, setBbox] = useState<string | null>(null);
  const [showDensity, setShowDensity] = useState(true);
  const [showPoints, setShowPoints] = useState(true);



  // Fetch filter options once
  useEffect(() => {
    geoService.getFilterOptions()
      .then(options => setFilterOptions(options))
      .catch(err => console.error("Failed to load filter options", err));
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const filters: CrimeMapFilters = {
          district_id: selectedDistrict || undefined,
          crime_type_id: selectedCrime || undefined,
          investigation_id: selectedInvestigation || undefined,
          start_date: startDate ? new Date(startDate).toISOString() : undefined,
          end_date: endDate ? new Date(endDate).toISOString() : undefined,
        };

        const [crimes, density] = await Promise.all([
          geoService.getCrimeLocations({ ...filters, bbox: bbox || undefined, limit: 1000 }),
          geoService.getCrimeDensity({ ...filters, bbox: bbox || undefined })
        ]);
        setGeoData(crimes);
        setDensityData(density);
      } catch (err) {
        console.error("Failed to load geospatial data", err);
        setError("Unable to load geospatial intelligence.");
      } finally {
        setIsLoading(false);
      }
    };
    
    const timer = setTimeout(() => {
      fetchData();
    }, 300);
    return () => clearTimeout(timer);
  }, [bbox, selectedDistrict, selectedCrime, selectedInvestigation, startDate, endDate]);

  const handleResetFilters = () => {
    setSelectedDistrict("");
    setSelectedCrime("");
    setSelectedInvestigation("");
    setStartDate("");
    setEndDate("");
  };

  const handleMapMove = useCallback((e: any) => {
    const bounds = e.target.getBounds();
    if (bounds) {
      const newBbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;
      setBbox(newBbox);
    }
  }, []);

  const handleMapClick = (event: any) => {
    const feature = event.features && event.features[0];
    if (feature && feature.properties) {
      if (feature.layer?.id === "density-fill-layer") {
        setActiveCluster({
          cluster_id: feature.properties.cluster_id,
          crime_count: feature.properties.crime_count,
          density_score: feature.properties.density_score
        });
        setActiveCrime(null);
      } else if (feature.layer?.id === "crimes-layer") {
        setActiveCrime(feature.properties as CrimeProperties);
        setActiveCluster(null);
      }
    } else {
      setActiveCrime(null);
      setActiveCluster(null);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 h-full flex flex-col">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">Geospatial Intelligence Map</h1>
            <p className="text-sm text-[#9A9A9A]">Observed crime locations and spatial density analysis</p>
          </div>
        </div>

        {/* Filters and Controls Toolbar */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 bg-[#080808]/40 border border-[#222222] p-4 rounded-2xl items-end">
          <div className="md:col-span-2 space-y-1.5">
            <label className="text-[10px] font-bold text-[#9A9A9A] uppercase tracking-wider flex items-center gap-1">
              <MapPin className="h-3 w-3 text-[#10B981]" /> District
            </label>
            <select
              className="w-full bg-[#050505] border border-slate-850 rounded-xl px-3 py-2 text-xs text-[#F5F5F5] focus:outline-none focus:ring-1 focus:ring-[#10B981]"
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
            >
              <option value="">All Districts</option>
              {filterOptions?.districts.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>

          <div className="md:col-span-2 space-y-1.5">
            <label className="text-[10px] font-bold text-[#9A9A9A] uppercase tracking-wider flex items-center gap-1">
              <Sliders className="h-3 w-3 text-indigo-400" /> Crime Type
            </label>
            <select
              className="w-full bg-[#050505] border border-slate-850 rounded-xl px-3 py-2 text-xs text-[#F5F5F5] focus:outline-none focus:ring-1 focus:ring-[#10B981]"
              value={selectedCrime}
              onChange={(e) => setSelectedCrime(e.target.value)}
            >
              <option value="">All Crime Types</option>
              {filterOptions?.crime_types.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>

          <div className="md:col-span-2 space-y-1.5">
            <label className="text-[10px] font-bold text-[#9A9A9A] uppercase tracking-wider flex items-center gap-1">
              <ShieldAlert className="h-3 w-3 text-rose-500" /> Investigation
            </label>
            <select
              className="w-full bg-[#050505] border border-slate-850 rounded-xl px-3 py-2 text-xs text-[#F5F5F5] focus:outline-none focus:ring-1 focus:ring-[#10B981]"
              value={selectedInvestigation}
              onChange={(e) => setSelectedInvestigation(e.target.value)}
              disabled={!filterOptions || filterOptions.investigations.length === 0}
            >
              <option value="">
                {!filterOptions || filterOptions.investigations.length === 0 ? "No investigations available" : "All Investigations"}
              </option>
              {filterOptions?.investigations.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
            </select>
          </div>

          <div className="md:col-span-3 space-y-1.5">
            <label className="text-[10px] font-bold text-[#9A9A9A] uppercase tracking-wider flex items-center gap-1">
              <Calendar className="h-3 w-3 text-amber-500" /> Date Range
            </label>
            <div className="flex gap-2">
              <input 
                type="date"
                className="w-full bg-[#050505] border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-[#F5F5F5] focus:outline-none focus:ring-1 focus:ring-[#10B981]"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
              <span className="text-[#666666] self-center">→</span>
              <input 
                type="date"
                className="w-full bg-[#050505] border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-[#F5F5F5] focus:outline-none focus:ring-1 focus:ring-[#10B981]"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          <div className="md:col-span-1 flex items-end">
            <button
              onClick={handleResetFilters}
              className="w-full py-2 bg-[#0D0D0D] hover:bg-[#111111] text-[#F5F5F5] text-xs font-bold rounded-xl transition-colors"
            >
              Reset
            </button>
          </div>

          <div className="md:col-span-2 space-y-1.5">
            <label className="text-[10px] font-bold text-[#9A9A9A] uppercase tracking-wider flex items-center gap-1">
              <Layers className="h-3 w-3 text-emerald-400" /> Layers
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setShowDensity(!showDensity)}
                className={`flex-1 py-2 rounded-xl text-[10px] font-bold border transition-colors ${
                  showDensity ? "bg-amber-500/10 border-amber-500/30 text-amber-400" : "bg-[#050505] border-slate-850 text-[#666666]"
                }`}
              >Density</button>
              <button
                onClick={() => setShowPoints(!showPoints)}
                className={`flex-1 py-2 rounded-xl text-[10px] font-bold border transition-colors ${
                  showPoints ? "bg-red-500/10 border-red-500/30 text-red-400" : "bg-[#050505] border-slate-850 text-[#666666]"
                }`}
              >Points</button>
            </div>
          </div>
        </div>

        {/* Map Viewport Area */}
        <div className="flex-1 min-h-[500px] grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          <div className="lg:col-span-8 bg-[#050505]/40 border border-[#222222] rounded-2xl p-2 relative overflow-hidden h-[500px]">
            {isLoading && (
              <div className="absolute inset-0 z-10 flex items-center justify-center bg-[#050505]/50 backdrop-blur-sm">
                 <div className="flex items-center gap-2 bg-[#080808] border border-[#222222] px-4 py-2 rounded-full shadow-lg">
                   <Loader2 className="h-4 w-4 text-[#10B981] animate-spin" />
                   <span className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Loading geospatial intelligence...</span>
                 </div>
              </div>
            )}
            {error && (
               <div className="absolute inset-0 z-10 flex items-center justify-center bg-[#050505]/50 backdrop-blur-sm">
                 <div className="flex items-center gap-2 bg-red-950/40 border border-red-900 px-4 py-3 rounded-lg shadow-lg max-w-sm text-center flex-col">
                   <ShieldAlert className="h-6 w-6 text-red-500 mb-2" />
                   <span className="text-sm font-bold text-red-400 uppercase tracking-widest">{error}</span>
                 </div>
               </div>
            )}
            
            <Map
              initialViewState={{ longitude: 76.6, latitude: 15.3, zoom: 5.5 }}
              mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
              interactive={true}
              onMoveEnd={handleMapMove}
              onClick={handleMapClick}
              interactiveLayerIds={["crimes-layer", "density-fill-layer"]}
              cursor="pointer"
            >
              {/* Density polygon layer — rendered below points */}
              {showDensity && densityData && !error && (
                <Source id="density-source" type="geojson" data={densityData}>
                  <Layer 
                    id="density-fill-layer"
                    type="fill"
                    paint={{
                      "fill-color": [
                        "interpolate", ["linear"], ["get", "crime_count"],
                        5, "rgba(251, 191, 36, 0.15)",
                        15, "rgba(245, 158, 11, 0.3)",
                        30, "rgba(239, 68, 68, 0.4)",
                        50, "rgba(220, 38, 38, 0.5)"
                      ],
                      "fill-opacity": 0.6
                    }}
                  />
                  <Layer 
                    id="density-outline-layer"
                    type="line"
                    paint={{
                      "line-color": [
                        "interpolate", ["linear"], ["get", "crime_count"],
                        5, "rgba(251, 191, 36, 0.5)",
                        30, "rgba(239, 68, 68, 0.7)",
                        50, "rgba(220, 38, 38, 0.9)"
                      ],
                      "line-width": 1.5
                    }}
                  />
                </Source>
              )}

              {/* Crime points layer — rendered on top */}
              {showPoints && geoData && !error && (
                <Source id="crimes-source" type="geojson" data={geoData}>
                  <Layer 
                    id="crimes-layer"
                    type="circle"
                    paint={{
                      "circle-radius": [
                        "interpolate", ["linear"], ["zoom"],
                        5, 2,
                        10, 5,
                        15, 10
                      ],
                      "circle-color": "#ef4444",
                      "circle-stroke-width": 1,
                      "circle-stroke-color": "#1e293b",
                      "circle-opacity": 0.7
                    }}
                  />
                </Source>
              )}
            </Map>
            
            {/* Density legend */}
            {showDensity && densityData && densityData.features.length > 0 && (
              <div className="absolute bottom-4 left-4 z-10">
                <div className="bg-[#050505]/90 backdrop-blur-sm border border-[#222222] px-3 py-2 rounded-lg shadow-lg">
                  <span className="text-[9px] font-bold text-[#9A9A9A] uppercase tracking-widest block mb-1.5">Observed Crime Density</span>
                  <div className="flex items-center gap-1.5 text-[9px]">
                    <div className="w-3 h-3 rounded-sm bg-amber-500/30 border border-amber-500/50" />
                    <span className="text-[#9A9A9A]">Lower</span>
                    <div className="w-8 h-1.5 bg-gradient-to-r from-amber-500/30 via-orange-500/40 to-red-600/50 rounded-full mx-1" />
                    <div className="w-3 h-3 rounded-sm bg-red-600/50 border border-red-500/70" />
                    <span className="text-[#9A9A9A]">Higher</span>
                  </div>
                  <span className="text-[8px] text-[#666666] mt-1 block">Method: PostGIS ST_ClusterDBSCAN</span>
                </div>
              </div>
            )}
            
            {!isLoading && !error && geoData?.features?.length === 0 && (
              <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10">
                 <div className="bg-[#080808]/90 backdrop-blur-sm border border-[#222222] px-4 py-2 rounded-full shadow-lg">
                   <span className="text-xs font-semibold text-[#9A9A9A]">No verified crime locations available for the current view.</span>
                 </div>
              </div>
            )}
          </div>

          {/* Right panel: Active Feature Details */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            <div className="flex-1 bg-[#080808]/40 border border-[#222222] p-5 rounded-2xl flex flex-col min-h-[300px]">
              {activeCluster ? (
                <div className="space-y-4 flex-1 flex flex-col">
                  <div className="border-b border-[#222222] pb-3">
                    <span className="text-[9px] font-bold text-amber-400 uppercase tracking-widest block font-mono">
                      Observed Spatial Cluster
                    </span>
                    <h3 className="font-bold text-white text-base mt-0.5 leading-snug">
                      Cluster #{activeCluster.cluster_id}
                    </h3>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-[#050505]/50 p-2.5 rounded-lg border border-slate-850 text-center">
                      <span className="text-[9px] text-[#666666] block uppercase font-bold">Observed Crimes</span>
                      <span className="text-lg font-extrabold text-amber-400">{activeCluster.crime_count}</span>
                    </div>
                    <div className="bg-[#050505]/50 p-2.5 rounded-lg border border-slate-850 text-center">
                      <span className="text-[9px] text-[#666666] block uppercase font-bold">Density Score</span>
                      <span className="text-lg font-extrabold text-[#F5F5F5]">{activeCluster.density_score}</span>
                    </div>
                  </div>
                  <div className="space-y-1 text-xs">
                    <span className="text-[10px] font-bold text-[#9A9A9A] uppercase block">Spatial Method</span>
                    <span className="font-semibold text-[#F5F5F5] block">PostGIS ST_ClusterDBSCAN (eps=0.05°, minpoints=5)</span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <span className="text-[10px] font-bold text-[#9A9A9A] uppercase block">Geometry</span>
                    <span className="font-semibold text-[#F5F5F5] block">Convex Hull of clustered crime locations</span>
                  </div>
                  <div className="space-y-1 text-xs bg-[#050505]/40 p-3 rounded-lg border border-slate-850 leading-relaxed text-[#666666]">
                    <span className="text-[9px] font-bold text-[#666666] uppercase block mb-1">System Note</span>
                    This is an observed spatial density cluster, not a predictive hotspot. The boundary represents the convex hull of {activeCluster.crime_count} real crime records spatially concentrated within ~5.5km of each other.
                  </div>
                </div>
              ) : activeCrime ? (
                <div className="space-y-4 flex-1 flex flex-col">
                  <div className="border-b border-[#222222] pb-3">
                    <span className="text-[9px] font-bold text-[#10B981] uppercase tracking-widest block font-mono">
                      {activeCrime.district || "Unknown District"}
                    </span>
                    <h3 className="font-bold text-white text-base mt-0.5 leading-snug">
                      {activeCrime.title || activeCrime.fir_number || "Unspecified Crime"}
                    </h3>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-[#050505]/50 p-2.5 rounded-lg border border-slate-850 text-center">
                      <span className="text-[9px] text-[#666666] block uppercase font-bold">FIR Number</span>
                      <span className="text-sm font-semibold text-[#F5F5F5] mt-1 block">
                        {activeCrime.fir_number || "N/A"}
                      </span>
                    </div>
                    <div className="bg-[#050505]/50 p-2.5 rounded-lg border border-slate-850 text-center">
                      <span className="text-[9px] text-[#666666] block uppercase font-bold">Status</span>
                      <span className="text-sm font-semibold text-[#F5F5F5] mt-1 block">
                        {activeCrime.status || "Unknown"}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-1 text-xs">
                    <span className="text-[10px] font-bold text-[#9A9A9A] uppercase block">Crime Type</span>
                    <span className="font-semibold text-[#F5F5F5] block">{activeCrime.crime_type || "N/A"}</span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <span className="text-[10px] font-bold text-[#9A9A9A] uppercase block">Police Station</span>
                    <span className="font-semibold text-[#F5F5F5] block">{activeCrime.station || "N/A"}</span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <span className="text-[10px] font-bold text-[#9A9A9A] uppercase block">Occurrence Date</span>
                    <span className="font-semibold text-[#F5F5F5] block">
                      {activeCrime.occurrence_date 
                        ? new Date(activeCrime.occurrence_date).toLocaleString()
                        : "N/A"}
                    </span>
                  </div>
                  {activeCrime.estimated_loss && (
                    <div className="space-y-1 text-xs">
                      <span className="text-[10px] font-bold text-[#9A9A9A] uppercase block">Estimated Loss</span>
                      <span className="font-semibold text-[#F5F5F5] block">₹{activeCrime.estimated_loss.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="space-y-1 text-xs bg-[#050505]/40 p-3 rounded-lg border border-slate-850 leading-relaxed text-[#666666]">
                    <span className="text-[9px] font-bold text-[#666666] uppercase block mb-1">System Note</span>
                    This is a verified crime location sourced directly from real database records.
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center text-[#666666] space-y-2">
                  <MapIcon className="h-8 w-8 text-[#666666]" />
                  <p className="text-xs font-semibold">Select a Feature</p>
                  <p className="text-[10px] text-[#666666] max-w-[200px]">Click on a crime point or density region to view observed intelligence details.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
