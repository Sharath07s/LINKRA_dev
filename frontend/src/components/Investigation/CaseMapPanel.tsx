"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState, useRef } from "react";
import { Map, Layers, Target, Navigation } from "lucide-react";
// Dynamic import for maplibregl is required in Next.js since it accesses the window object
// Using a placeholder visual representation for the datathon context if maplibre isn't available

interface CaseMapPanelProps {
  investigationId: string;
}

export default function CaseMapPanel({ investigationId }: CaseMapPanelProps) {
  const [locations, setLocations] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLocations = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.get(`/investigations/${investigationId}/locations`);
        if (res.status === 200) {
          const data = res.data;
          setLocations(data);
        }
      } catch (err) {
        console.warn("Failed to fetch locations:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (investigationId) {
      fetchLocations();
    }
  }, [investigationId]);

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full overflow-hidden relative group">
      {/* Overlay UI Controls */}
      <div className="absolute top-4 left-4 right-4 z-10 flex justify-between items-start pointer-events-none">
        <div className="bg-slate-950/80 backdrop-blur-md border border-slate-800 p-2.5 rounded-xl pointer-events-auto shadow-lg flex items-center gap-2">
          <Map className="h-4 w-4 text-blue-400" />
          <h3 className="text-xs font-bold text-white tracking-wide uppercase">Geographic Intelligence</h3>
        </div>
        
        <div className="flex flex-col gap-2 pointer-events-auto">
          <button className="p-2 rounded-lg bg-slate-950/80 backdrop-blur-md border border-slate-800 text-slate-400 hover:text-white hover:border-blue-500/50 transition-all shadow-lg">
            <Layers className="h-4 w-4" />
          </button>
          <button className="p-2 rounded-lg bg-slate-950/80 backdrop-blur-md border border-slate-800 text-slate-400 hover:text-white hover:border-blue-500/50 transition-all shadow-lg">
            <Target className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="absolute bottom-4 left-4 z-10 pointer-events-auto">
        <div className="bg-slate-950/80 backdrop-blur-md border border-slate-800 p-3 rounded-xl shadow-lg flex flex-col gap-2">
          <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Active Layers</span>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-[10px] text-slate-300 font-semibold">Incident Locations</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-[10px] text-slate-300 font-semibold">Suspect Sightings</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-[10px] text-slate-300 font-semibold">Related FIRs</span>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 bg-slate-950/50 relative overflow-hidden flex items-center justify-center">
        {/* Abstract Map Grid Background representing map tiles */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(30,41,59,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(30,41,59,0.2)_1px,transparent_1px)] bg-[size:40px_40px]" />
        
        {isLoading ? (
          <div className="z-20 bg-slate-900/80 border border-slate-800 px-4 py-2 rounded-full flex items-center gap-2 backdrop-blur-sm">
            <Navigation className="h-4 w-4 text-blue-400 animate-spin" />
            <span className="text-xs font-bold text-blue-400 tracking-widest uppercase">Initializing Map Engine...</span>
          </div>
        ) : locations?.features?.length > 0 ? (
          <div className="z-20 w-full h-full relative">
            {/* Render coordinates as glowing dots on the abstract grid */}
            {locations.features.map((f: any, idx: number) => {
              // Map lon/lat to relative percentages for abstract display
              const left = `${50 + (f.geometry.coordinates[0] % 1) * 100}%`;
              const top = `${50 + (f.geometry.coordinates[1] % 1) * 100}%`;
              
              return (
                <div 
                  key={f.properties.id || idx}
                  className="absolute w-4 h-4 -ml-2 -mt-2 group/marker cursor-pointer"
                  style={{ left, top }}
                >
                  <div className="w-full h-full bg-red-500 rounded-full animate-pulse opacity-70" />
                  <div className="absolute inset-1 bg-red-400 rounded-full" />
                  
                  {/* Tooltip */}
                  <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-48 p-2 bg-slate-900 border border-slate-700 rounded-lg shadow-xl opacity-0 group-hover/marker:opacity-100 transition-opacity pointer-events-none z-30">
                    <span className="block text-[10px] font-bold text-slate-400 mb-1">{f.properties.type}</span>
                    <span className="block text-xs font-semibold text-white">{f.properties.title}</span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="z-20 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 rounded-full bg-slate-800/50 flex items-center justify-center border border-slate-700/50 mb-4">
               <Navigation className="h-5 w-5 text-slate-500" />
            </div>
            <h4 className="text-sm font-semibold text-slate-300 mb-1">No Verified Locations</h4>
            <p className="text-xs text-slate-500 max-w-[200px]">
              No geographic coordinates are currently associated with this investigation.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
