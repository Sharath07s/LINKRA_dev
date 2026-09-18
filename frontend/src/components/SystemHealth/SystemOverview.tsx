"use client";

import React from "react";
import { Activity, ShieldCheck, Clock } from "lucide-react";

export default function SystemOverview({ summary }: { summary: any }) {
  if (!summary) return <div suppressHydrationWarning className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const isDegraded = summary.system_status === "Degraded";

  return (
    <div className={`h-full bg-[#080808] border ${isDegraded ? 'border-amber-500/50' : 'border-emerald-500/50'} rounded-xl p-4 flex flex-col justify-between relative overflow-hidden`}>
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-[#9A9A9A] uppercase tracking-widest flex items-center gap-2">
          <Activity className={`h-4 w-4 ${isDegraded ? 'text-amber-500' : 'text-emerald-500'}`} /> Platform Status
        </h3>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${isDegraded ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'}`}>
          {summary.system_status}
        </span>
      </div>
      
      <div className="flex items-center gap-4 mt-2">
        <ShieldCheck className={`h-10 w-10 ${isDegraded ? 'text-amber-500' : 'text-emerald-500'}`} />
        <div>
          <p className="text-2xl font-black text-white tracking-widest uppercase">{summary.operational_components}/3</p>
          <p className="text-xs text-[#9A9A9A] font-mono">Core Engines Online</p>
        </div>
      </div>
      
      <div className="flex justify-between items-end mt-4">
        <div className="flex flex-col">
          <span className="text-[10px] text-[#666666] uppercase tracking-widest">Last Refresh</span>
          <span suppressHydrationWarning className="text-xs text-[#F5F5F5] font-mono flex items-center gap-1"><Clock className="h-3 w-3"/> {new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}
