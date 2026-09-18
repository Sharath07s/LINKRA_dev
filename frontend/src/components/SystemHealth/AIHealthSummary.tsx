"use client";

import React from "react";
import { Stethoscope } from "lucide-react";

export default function AIHealthSummary({ summary }: { summary: any }) {
  if (!summary) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const hasFailures = summary.failed_components && summary.failed_components.length > 0;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Stethoscope className="h-4 w-4 text-[#10B981]" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Diagnostic Recommendation</h3>
      </div>
      
      <div className="flex-1 p-4 flex flex-col justify-center">
        {hasFailures ? (
          <div className="bg-red-500/10 border border-red-500/20 rounded p-3">
            <span className="block text-[10px] font-bold text-red-500 uppercase tracking-widest mb-1">Failed Components Detected</span>
            <ul className="text-xs text-red-400 list-disc pl-4 mb-3 font-mono">
              {summary.failed_components?.map((f: string, i: number) => <li key={i}>{f} offline</li>)}
            </ul>
            <span className="block text-[10px] font-bold text-amber-500 uppercase tracking-widest mb-1">Recommended Action</span>
            <p className="text-sm text-[#F5F5F5]">{summary.recommended_action}</p>
          </div>
        ) : (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded p-4 text-center">
            <span className="block text-[10px] font-bold text-emerald-500 uppercase tracking-widest mb-2">System Nominal</span>
            <p className="text-sm text-[#F5F5F5]">{summary.recommended_action}</p>
          </div>
        )}
      </div>
    </div>
  );
}
