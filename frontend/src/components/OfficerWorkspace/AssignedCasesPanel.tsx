"use client";

import React from "react";
import { FolderOpen, MapPin, Calendar, ExternalLink } from "lucide-react";

export default function AssignedCasesPanel({ cases }: { cases: any[] }) {
  if (!cases || cases.length === 0) {
    return (
      <div suppressHydrationWarning className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl p-4 flex flex-col items-center justify-center opacity-70">
        <FolderOpen className="h-8 w-8 text-[#666666] mb-2" />
        <span className="text-sm font-bold text-[#9A9A9A]">No active cases assigned</span>
      </div>
    );
  }

  return (
    <div className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <FolderOpen className="h-4 w-4 text-[#10B981]" /> My Active Cases
        </h3>
        <span className="bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20 text-[10px] px-2 py-0.5 rounded font-mono">
          {cases.length} TOTAL
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {cases?.map((c) => (
          <div key={c.id} className="bg-[#050505] p-3 rounded-lg border border-[#222222] hover:border-[#2A2A2A] transition-colors cursor-pointer group">
            <div className="flex justify-between items-start mb-2">
              <span className="text-[10px] bg-[#0D0D0D] text-[#F5F5F5] px-1.5 py-0.5 rounded font-mono">
                {c.fir_number || c.id.substring(0,8).toUpperCase()}
              </span>
              <ExternalLink className="h-3 w-3 text-[#666666] group-hover:text-[#10B981]" />
            </div>
            <p className="text-xs font-medium text-[#F5F5F5] mb-3 line-clamp-2">{c.description || "No description provided"}</p>
            <div className="flex justify-between items-center text-[10px] text-[#666666]">
              <div className="flex items-center gap-1">
                <MapPin className="h-3 w-3" /> Location Pending
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" /> {new Date(c.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
