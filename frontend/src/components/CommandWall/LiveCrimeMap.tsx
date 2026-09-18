"use client";

import React from "react";
import { Map } from "lucide-react";

export default function LiveCrimeMap() {
  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10">
        <h3 className="text-xs font-bold text-white uppercase tracking-widest px-3 py-1 bg-[#050505]/80 rounded border border-[#222222] flex items-center gap-2 shadow-lg">
          <Map className="h-4 w-4 text-emerald-500" /> Tactical Sector Map
        </h3>
      </div>
      
      <div className="flex-1 w-full bg-[#0D0D0D] relative">
        {/* Abstract representation of a MapLibre integration */}
        <div className="absolute inset-0" style={{
           backgroundImage: `radial-gradient(circle at 30% 40%, rgba(16, 185, 129, 0.15) 0, transparent 40%), 
                             radial-gradient(circle at 70% 60%, rgba(239, 68, 68, 0.15) 0, transparent 40%)`
        }} />
        <div className="absolute inset-0 flex items-center justify-center opacity-30">
           <span className="text-xs font-mono text-[#9A9A9A] uppercase tracking-widest bg-[#080808] px-2 py-1 rounded">MapLibre Integration Required for Geospatial Rendering</span>
        </div>
      </div>
    </div>
  );
}
