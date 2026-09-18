"use client";

import React from "react";
import { FileWarning } from "lucide-react";

export default function DataQualityPanel({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <FileWarning className="h-4 w-4 text-amber-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Data Quality</h3>
      </div>
      
      <div className="flex-1 p-3 grid grid-cols-2 gap-2">
        <div className="bg-[#050505] p-2 rounded border border-[#222222] flex justify-between items-center">
          <span className="text-[10px] text-[#9A9A9A]">Missing Coords</span>
          <span className={`text-xs font-mono ${data.missing_coordinates > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>{data.missing_coordinates}</span>
        </div>
        <div className="bg-[#050505] p-2 rounded border border-[#222222] flex justify-between items-center">
          <span className="text-[10px] text-[#9A9A9A]">Missing Districts</span>
          <span className={`text-xs font-mono ${data.missing_districts > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>{data.missing_districts}</span>
        </div>
        <div className="bg-[#050505] p-2 rounded border border-[#222222] flex justify-between items-center">
          <span className="text-[10px] text-[#9A9A9A]">Orphan Nodes</span>
          <span className={`text-xs font-mono ${data.orphan_neo4j_nodes > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>{data.orphan_neo4j_nodes}</span>
        </div>
        <div className="bg-[#050505] p-2 rounded border border-[#222222] flex justify-between items-center">
          <span className="text-[10px] text-[#9A9A9A]">Duplicate FIRs</span>
          <span className={`text-xs font-mono ${data.duplicate_fir > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>{data.duplicate_fir}</span>
        </div>
      </div>
    </div>
  );
}
