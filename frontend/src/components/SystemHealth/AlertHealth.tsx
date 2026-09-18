"use client";

import React from "react";
import { ShieldAlert } from "lucide-react";

export default function AlertHealth({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 text-amber-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Alert Engine</h3>
      </div>
      
      <div className="flex-1 p-4 flex flex-col justify-center gap-4">
        <div className="flex justify-between items-center">
          <span className="text-xs text-[#9A9A9A] font-bold uppercase tracking-widest">Engine Status</span>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">{data.status}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-[#F5F5F5]">Open Alerts</span>
          <span className="text-lg font-mono text-white">{data.open_alerts}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-[#F5F5F5]">Critical Priority</span>
          <span className="text-lg font-mono text-red-400">{data.critical_alerts}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs text-[#F5F5F5]">Generated Today</span>
          <span className="text-lg font-mono text-amber-400">{data.alerts_today}</span>
        </div>
      </div>
    </div>
  );
}
