"use client";

import React from "react";
import { MapPin } from "lucide-react";

interface AlertMapOverlayProps {
  alerts: any[];
}

export default function AlertMapOverlay({ alerts }: AlertMapOverlayProps) {
  // A visual placeholder for a MapLibre overlay.
  // Instead of rendering a full heavy map if we don't have geo-coords for every alert, 
  // we render a tactical grid layout showing affected districts.
  
  const uniqueDistricts = Array.from(new Set(alerts?.map(a => a.district)?.filter(d => d !== "Multiple")));

  if (uniqueDistricts.length === 0) {
    return (
      <div className="h-full bg-[#080808]/30 border border-[#222222] rounded-xl flex items-center justify-center">
        <span className="text-xs font-bold text-[#666666] uppercase tracking-widest">No Geographic Intelligence</span>
      </div>
    );
  }

  return (
    <div className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl p-4 relative overflow-hidden">
       {/* Tactical grid background */}
       <div className="absolute inset-0" style={{
         backgroundImage: `linear-gradient(rgba(51, 65, 85, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(51, 65, 85, 0.1) 1px, transparent 1px)`,
         backgroundSize: '20px 20px'
       }} />
       
       <div className="relative z-10">
         <h4 className="text-xs font-bold text-[#9A9A9A] uppercase tracking-widest mb-4">Affected Sectors</h4>
         
         <div className="flex flex-wrap gap-2">
           {uniqueDistricts?.map(district => {
             const distAlerts = alerts?.filter(a => a.district === district);
             const hasCritical = distAlerts.some(a => a.severity === 'CRITICAL');
             
             return (
               <div key={district} className={`px-3 py-2 rounded border flex items-center gap-2 ${
                 hasCritical ? "bg-red-500/10 border-red-500/30 text-red-400" : "bg-[#0D0D0D] border-[#2A2A2A] text-[#F5F5F5]"
               }`}>
                 <MapPin className="h-3 w-3" />
                 <span className="text-xs font-bold">{district}</span>
                 <span className="text-[10px] bg-[#050505] px-1.5 rounded-sm">{distAlerts.length}</span>
               </div>
             );
           })}
         </div>
       </div>
    </div>
  );
}
