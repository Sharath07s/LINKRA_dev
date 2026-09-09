"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Map as MapIcon, Layers } from "lucide-react";

export default function CrimeHotspotsMap() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHotspots = async () => {
      try {
        const res = await apiClient.get(`/executive/hotspots`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch hotspots:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHotspots();
  }, []);

  if (isLoading) return <div className="h-full bg-slate-900/40 border border-slate-800 rounded-2xl animate-pulse"></div>;
  if (!data) return null;

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full overflow-hidden relative">
      <div className="absolute top-4 left-4 right-4 z-10 flex justify-between items-start pointer-events-none">
        <div className="bg-slate-950/80 backdrop-blur-md border border-slate-800 p-2.5 rounded-xl pointer-events-auto shadow-lg flex items-center gap-2">
          <MapIcon className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white tracking-wide uppercase">State Heatmap</h3>
        </div>
        
        <div className="bg-slate-950/80 backdrop-blur-md border border-slate-800 p-2.5 rounded-xl pointer-events-auto shadow-lg flex flex-col gap-2">
          <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500 border-b border-slate-800 pb-1 mb-1">Top Crime Regions</span>
          {data.top_hotspots?.map((h: any, idx: number) => (
            <div key={idx} className="flex justify-between items-center gap-4">
              <span className="text-xs font-bold text-white">{h.district}</span>
              <span className="text-[10px] font-mono text-red-400">{h.crime_count} cases</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 bg-slate-950/80 relative overflow-hidden flex items-center justify-center">
        {/* Abstract Map Interface for Executive Dashboard */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(30,41,59,0.3)_1px,transparent_1px),linear-gradient(90deg,rgba(30,41,59,0.3)_1px,transparent_1px)] bg-[size:40px_40px]" />
        
        <div className="z-20 relative w-full h-full flex items-center justify-center">
           {/* Abstract Karnataka Outline / Heatmap blobs */}
           <div className="absolute w-64 h-64 bg-emerald-900/20 rounded-[40%_60%_70%_30%/40%_50%_60%_50%] blur-3xl opacity-50" />
           <div className="absolute w-32 h-32 bg-red-600/40 rounded-full blur-2xl top-1/4 left-1/3 animate-pulse" />
           <div className="absolute w-48 h-48 bg-amber-600/30 rounded-full blur-2xl bottom-1/4 right-1/3" />
           
           {/* Map UI overlays */}
           <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-slate-800">
             <Layers className="h-3 w-3 text-slate-400" />
             <span className="text-[9px] text-slate-400 font-bold uppercase">MapLibre GL JS Instance</span>
           </div>
        </div>
      </div>
    </div>
  );
}
