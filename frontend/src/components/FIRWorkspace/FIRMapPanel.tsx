"use client";

import React from "react";
import { Map } from "lucide-react";

interface FIRMapPanelProps {
  firId: string;
}

export default function FIRMapPanel({ firId }: FIRMapPanelProps) {
  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden relative group">
      <div className="absolute top-4 left-4 right-4 z-10 flex justify-between items-start pointer-events-none">
        <div className="bg-[#050505]/80 backdrop-blur-md border border-[#222222] p-2.5 rounded-xl pointer-events-auto shadow-lg flex items-center gap-2">
          <Map className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white tracking-wide uppercase">Incident Radius</h3>
        </div>
      </div>

      <div className="flex-1 bg-[#050505]/50 relative overflow-hidden flex items-center justify-center">
        {/* Abstract Map Grid Background representing map tiles */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(30,41,59,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(30,41,59,0.2)_1px,transparent_1px)] bg-[size:40px_40px]" />
        
        <div className="z-20 relative flex items-center justify-center">
          {/* Main Incident Ping */}
          <div className="absolute w-4 h-4 group/marker cursor-pointer z-30">
            <div className="w-full h-full bg-red-500 rounded-full animate-ping opacity-70" />
            <div className="absolute inset-1 bg-red-400 rounded-full" />
            <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-32 p-2 bg-[#080808] border border-[#2A2A2A] rounded-lg shadow-xl opacity-0 group-hover/marker:opacity-100 transition-opacity pointer-events-none text-center">
              <span className="block text-xs font-semibold text-white">Incident Zero</span>
            </div>
          </div>

          {/* Abstract Radius Circle */}
          <div className="w-48 h-48 rounded-full border border-red-500/30 bg-red-500/5 animate-pulse" />
          
          {/* Nearby Cluster Node */}
          <div className="absolute w-3 h-3 top-[-40px] right-[-60px] group/cluster cursor-pointer">
             <div className="w-full h-full bg-amber-500 rounded-full opacity-80" />
             <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-24 p-2 bg-[#080808] border border-[#2A2A2A] rounded-lg shadow-xl opacity-0 group-hover/cluster:opacity-100 transition-opacity pointer-events-none text-center">
              <span className="block text-[10px] font-semibold text-amber-400">Related Cluster</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
