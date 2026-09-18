"use client";

import React from "react";
import { Activity, MapPin } from "lucide-react";

export default function NearbyCrimesPanel() {
  return (
    <div className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <MapPin className="h-4 w-4 text-emerald-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Sector Activity (24H)</h3>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center opacity-50 relative p-4">
        {/* Placeholder for tactical map or list */}
        <div className="absolute inset-0" style={{
           backgroundImage: `radial-gradient(circle at center, rgba(16, 185, 129, 0.1) 0, transparent 70%)`
        }} />
        <Activity className="h-8 w-8 text-[#666666] mb-2 relative z-10" />
        <span className="text-xs font-bold text-[#9A9A9A] uppercase relative z-10 text-center">No major incidents detected<br/>in your immediate vicinity.</span>
      </div>
    </div>
  );
}
