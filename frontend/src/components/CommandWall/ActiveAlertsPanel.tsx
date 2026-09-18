"use client";

import React from "react";
import { AlertTriangle, ShieldAlert } from "lucide-react";

export default function ActiveAlertsPanel({ alerts }: { alerts: any[] }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="h-full bg-[#080808] border border-[#222222] rounded-xl p-4 flex items-center justify-center">
        <span className="text-xs font-mono text-[#666666] uppercase tracking-widest">0 Active Alerts</span>
      </div>
    );
  }

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-amber-500" /> Active Priority Alerts
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {alerts?.map(a => (
          <div key={a.id} className="p-2 border border-[#222222] rounded bg-[#050505] flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <span className={`text-[10px] font-bold uppercase tracking-widest ${a.severity === 'CRITICAL' ? 'text-red-500' : 'text-amber-500'}`}>
                {a.type}
              </span>
              <span className="text-[9px] text-[#666666] font-mono">{a.district}</span>
            </div>
            <p className="text-xs text-[#F5F5F5] truncate">{a.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
