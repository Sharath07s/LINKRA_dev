"use client";

import React from "react";
import { Webhook, Activity } from "lucide-react";

export default function APIHealth({ apis }: { apis: any[] }) {
  if (!apis) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Webhook className="h-4 w-4 text-indigo-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Internal APIs</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {apis?.map((api, i) => (
          <div key={i} className="bg-[#050505] border border-[#222222] rounded p-2 flex flex-col gap-1">
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-mono text-[#9A9A9A] truncate w-3/4">{api.endpoint}</span>
              <span className="text-[10px] font-mono text-emerald-400">{api.latency_ms}ms</span>
            </div>
            <div className="flex items-center gap-1">
              <Activity className="h-3 w-3 text-emerald-500" />
              <span className="text-[9px] uppercase tracking-widest text-emerald-500">{api.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
