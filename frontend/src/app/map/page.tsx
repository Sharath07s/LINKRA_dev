"use client";

import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { 
  Filter, Layers, MapPin, Calendar, Sliders, ShieldAlert, Activity, ChevronRight, Maximize2, Minimize2, Info
} from "lucide-react";
import Map, { Source, Layer, Marker } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

const HOTSPOTS = [
  { id: "h1", district: "Bengaluru City", locationName: "Indiranagar - Halasuru Sector", lat: 12.9784, lng: 77.6408, crimeCount: 18, threatScore: 9.4, riskLevel: "High", dominantCrime: "Cyber Jackpotting / Phishing", notes: "Correlated activity detected primarily during nocturnal hours (01:00 - 04:00)." },
  { id: "h2", district: "Mysuru", locationName: "Vidyaranyapuram - Kuvempunagar Axis", lat: 12.2831, lng: 76.6346, crimeCount: 11, threatScore: 7.8, riskLevel: "Medium", dominantCrime: "House Breaking by Night", notes: "Concentrated around locked residential properties. MO involves rear window access via pry tools." },
  { id: "h3", district: "Mangaluru", locationName: "Hampankatta - Port Area", lat: 12.8698, lng: 74.8430, crimeCount: 9, threatScore: 8.2, riskLevel: "High", dominantCrime: "Digital Ransomware Extortion", notes: "Targeting commercial networks and banking terminals. IP tracking points to cross-state proxy nodes." },
  { id: "h4", district: "Kalaburagi", locationName: "Station Bazaar Ward", lat: 17.3323, lng: 76.8378, crimeCount: 14, threatScore: 8.6, riskLevel: "High", dominantCrime: "Property Larceny & Smuggling", notes: "High concentration of retail cargo thefts close to regional distribution terminals." }
];

export default function CrimeMapPage() {
  const [selectedDistrict, setSelectedDistrict] = useState("All Districts");
  const [selectedCrime, setSelectedCrime] = useState("All Crimes");
  const [selectedRange, setSelectedRange] = useState("Last 30 Days");
  
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showClusters, setShowClusters] = useState(true);
  const [showStations, setShowStations] = useState(false);
  const [activeHotspot, setActiveHotspot] = useState<any>(null);

  const districtsList = ["All Regions", "Bengaluru City", "Mysuru", "Mangaluru", "Hubballi-Dharwad", "Belagavi", "Kalaburagi"];
  const crimeTypesList = ["All Crimes", "House Breaking", "Cyber Fraud", "Vehicle Theft", "Larceny"];

  const filteredHotspots = HOTSPOTS?.filter(h => {
    if (selectedDistrict !== "All Districts" && h.district !== selectedDistrict) return false;
    if (selectedCrime !== "All Crimes" && !h.dominantCrime.includes(selectedCrime.replace("All Crimes", ""))) return false;
    return true;
  });

  const geojson = {
    type: "FeatureCollection" as const,
    features: filteredHotspots?.map(h => ({
      type: "Feature" as const,
      properties: { threatScore: h.threatScore, id: h.id },
      geometry: { type: "Point" as const, coordinates: [h.lng, h.lat] }
    }))
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 h-full flex flex-col">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">Geospatial Intelligence Map</h1>
            <p className="text-sm text-slate-400">District threat analytics, spatiotemporal clustering, and police station boundaries</p>
          </div>
          <div className="flex items-center gap-1.5 rounded-full bg-red-500/10 border border-red-500/20 px-3 py-1 text-[10px] font-bold text-red-400">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500"></span>
            </span>
            <span>HIGH RISK FLASHES</span>
          </div>
        </div>

        {/* Filters and Controls Toolbar */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 bg-slate-900/40 border border-slate-800 p-4 rounded-2xl">
          <div className="md:col-span-3 space-y-1.5">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <MapPin className="h-3 w-3 text-blue-500" /> District Sector
            </label>
            <select
              className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
            >
              {districtsList?.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div className="md:col-span-3 space-y-1.5">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Sliders className="h-3 w-3 text-indigo-400" /> Crime Classification
            </label>
            <select
              className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={selectedCrime}
              onChange={(e) => setSelectedCrime(e.target.value)}
            >
              {crimeTypesList?.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div className="md:col-span-3 space-y-1.5">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Calendar className="h-3 w-3 text-amber-500" /> Temporal Range
            </label>
            <select
              className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={selectedRange}
              onChange={(e) => setSelectedRange(e.target.value)}
            >
              <option>Last 30 Days</option>
              <option>Last 6 Months</option>
              <option>Year-To-Date</option>
            </select>
          </div>

          <div className="md:col-span-3 space-y-1.5">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Layers className="h-3 w-3 text-emerald-400" /> Intelligence Overlays
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setShowHeatmap(!showHeatmap)}
                className={`flex-1 py-2 rounded-xl text-[10px] font-bold border transition-colors ${
                  showHeatmap ? "bg-red-500/10 border-red-500/30 text-red-400" : "bg-slate-950 border-slate-850 text-slate-500"
                }`}
              >Heatmap</button>
              <button
                onClick={() => setShowClusters(!showClusters)}
                className={`flex-1 py-2 rounded-xl text-[10px] font-bold border transition-colors ${
                  showClusters ? "bg-blue-500/10 border-blue-500/30 text-blue-400" : "bg-slate-950 border-slate-850 text-slate-500"
                }`}
              >Clusters</button>
            </div>
          </div>
        </div>

        {/* Map Viewport Area */}
        <div className="flex-1 min-h-[500px] grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          <div className="lg:col-span-8 bg-slate-950/40 border border-slate-800 rounded-2xl p-2 relative overflow-hidden h-[500px]">
            <Map
              initialViewState={{ longitude: 76.6, latitude: 15.3, zoom: 5.5 }}
              mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
              interactive={true}
            >
              {showHeatmap && (
                <Source type="geojson" data={geojson}>
                  <Layer 
                    id="heatmap"
                    type="heatmap"
                    paint={{
                      "heatmap-weight": ["interpolate", ["linear"], ["get", "threatScore"], 0, 0, 10, 1],
                      "heatmap-intensity": 1,
                      "heatmap-color": [
                        "interpolate", ["linear"], ["heatmap-density"],
                        0, "rgba(33,102,172,0)",
                        0.2, "rgb(103,169,207)",
                        0.4, "rgb(209,229,240)",
                        0.6, "rgb(253,219,199)",
                        0.8, "rgb(239,138,98)",
                        1, "rgb(178,24,43)"
                      ],
                      "heatmap-radius": 30,
                      "heatmap-opacity": 0.8
                    }}
                  />
                </Source>
              )}

              {showClusters && filteredHotspots?.map(h => (
                <Marker key={h.id} longitude={h.lng} latitude={h.lat} anchor="center" onClick={(e) => {
                  e.originalEvent.stopPropagation();
                  setActiveHotspot(h);
                }}>
                  <div className="relative flex h-6 w-6 items-center justify-center cursor-pointer group">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <div className="relative inline-flex rounded-full h-4 w-4 bg-red-600 border-2 border-slate-900 group-hover:scale-125 transition-transform" />
                  </div>
                </Marker>
              ))}
            </Map>
          </div>

          {/* Right panel: Active Hotspot details / sidebar */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-2xl">
              <h4 className="font-bold text-white text-sm uppercase tracking-wider mb-3">Threat Indexes</h4>
              <div className="space-y-3 text-xs">
                <div className="flex items-start gap-2.5 p-2 bg-red-950/10 border border-red-900/30 rounded-xl">
                  <span className="h-2 w-2 rounded-full bg-red-500 shrink-0 mt-1.5 animate-pulse" />
                  <div>
                    <span className="font-bold text-red-400 block">CRITICAL THREAT ZONE (&gt;8.0)</span>
                    <span className="text-[10px] text-slate-455 text-slate-400">High density clusters. Immediate proactive patrols required.</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex-1 bg-slate-900/40 border border-slate-800 p-5 rounded-2xl flex flex-col min-h-[300px]">
              {activeHotspot ? (
                <div className="space-y-4 flex-1 flex flex-col">
                  <div className="border-b border-slate-800 pb-3">
                    <span className="text-[9px] font-bold text-blue-400 uppercase tracking-widest block font-mono">
                      {activeHotspot.district} Sector
                    </span>
                    <h3 className="font-bold text-white text-base mt-0.5 leading-snug">{activeHotspot.locationName}</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-850 text-center">
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Threat Score</span>
                      <span className="text-lg font-extrabold text-red-400">{activeHotspot.threatScore} / 10</span>
                    </div>
                    <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-850 text-center">
                      <span className="text-[9px] text-slate-500 block uppercase font-bold">Cases Pinned</span>
                      <span className="text-lg font-extrabold text-slate-200">{activeHotspot.crimeCount}</span>
                    </div>
                  </div>
                  <div className="space-y-1 text-xs">
                    <span className="text-[10px] font-bold text-slate-400 uppercase block">Dominant MO Mode</span>
                    <span className="font-semibold text-slate-300 block">{activeHotspot.dominantCrime}</span>
                  </div>
                  <div className="space-y-1 text-xs bg-slate-950/40 p-3 rounded-lg border border-slate-850 leading-relaxed text-slate-300">
                    <span className="text-[9px] font-bold text-slate-500 uppercase block">Field Intelligence Note</span>
                    {activeHotspot.notes}
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 space-y-2">
                  <Maximize2 className="h-8 w-8 text-slate-600" />
                  <p className="text-xs font-semibold">Select a District Sector or Cluster Node</p>
                  <p className="text-[10px] text-slate-500 max-w-[180px]">Click on the map highlights to view spatiotemporal intelligence</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
