"use client";

import React from "react";
import { Network } from "lucide-react";

export default function NetworkIntelligencePanel({ networks }: { networks: any[] }) {
  if (!networks || networks.length === 0) {
    return (
      <div className="h-full bg-[#080808] border border-[#222222] rounded-xl p-4 flex items-center justify-center">
        <span className="text-xs font-mono text-[#666666] uppercase tracking-widest">Graph Isolated - No Critical Networks</span>
      </div>
    );
  }

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Network className="h-4 w-4 text-purple-500" /> Network Clusters (Neo4j)
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {networks?.map((n, i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-[#666666] font-mono w-4">{i+1}.</span>
              <span className="text-xs font-bold text-[#F5F5F5]">{n.network} Cluster</span>
            </div>
            <span className="text-[10px] font-mono text-purple-400 bg-purple-500/10 px-2 rounded border border-purple-500/20">
              DEGREE: {n.size}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
