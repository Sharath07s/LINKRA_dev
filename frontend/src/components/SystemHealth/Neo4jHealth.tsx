"use client";

import React from "react";
import { Network, CheckCircle, AlertTriangle } from "lucide-react";

export default function Neo4jHealth({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const isHealthy = data.status === "healthy";

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Network className="h-4 w-4 text-purple-500" /> Neo4j Graph DB
        </h3>
        {isHealthy ? <CheckCircle className="h-4 w-4 text-emerald-500" /> : <AlertTriangle className="h-4 w-4 text-amber-500" />}
      </div>
      
      <div className="flex-1 p-3 grid grid-cols-2 gap-3">
        <div className="bg-[#050505] rounded p-2 border border-[#222222]">
          <span className="block text-[10px] text-[#666666] uppercase tracking-widest mb-1">Latency</span>
          <span className={`text-lg font-mono ${data.latency_ms > 500 ? 'text-amber-500' : 'text-emerald-400'}`}>{data.latency_ms || 0}ms</span>
        </div>
        <div className="bg-[#050505] rounded p-2 border border-[#222222]">
          <span className="block text-[10px] text-[#666666] uppercase tracking-widest mb-1">Nodes</span>
          <span className="text-sm font-mono text-purple-400">{data.nodes || 0}</span>
        </div>
        
        <div className="col-span-2 mt-2 space-y-1">
          <div className="flex justify-between text-xs border-b border-[#222222] pb-1">
            <span className="text-[#9A9A9A]">Relationships</span>
            <span className="font-mono text-[#F5F5F5]">{data.relationships || 0}</span>
          </div>
          <div className="flex justify-between text-xs border-b border-[#222222] pb-1">
            <span className="text-[#9A9A9A]">Suspects</span>
            <span className="font-mono text-[#F5F5F5]">{data.suspects || 0}</span>
          </div>
          <div className="flex justify-between text-xs border-b border-[#222222] pb-1">
            <span className="text-[#9A9A9A]">Vehicles</span>
            <span className="font-mono text-[#F5F5F5]">{data.vehicles || 0}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-[#9A9A9A]">Locations</span>
            <span className="font-mono text-[#F5F5F5]">{data.locations || 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
