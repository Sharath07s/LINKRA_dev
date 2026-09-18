"use client";

import React from "react";
import { Network } from "lucide-react";

export default function OfficerNetworkView() {
  return (
    <div className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Network className="h-4 w-4 text-purple-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Local Network (Neo4j)</h3>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center opacity-50 relative p-4">
        {/* Placeholder for actual D3/ForceGraph network map of assigned cases */}
        <Network className="h-8 w-8 text-[#666666] mb-2 relative z-10" />
        <span className="text-xs font-bold text-[#9A9A9A] uppercase relative z-10 text-center">Graph initialization pending<br/>case selection</span>
      </div>
    </div>
  );
}
