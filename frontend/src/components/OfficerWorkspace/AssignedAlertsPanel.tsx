"use client";

import React from "react";
import { ShieldAlert, AlertTriangle } from "lucide-react";

export default function AssignedAlertsPanel({ alerts }: { alerts: any[] }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div suppressHydrationWarning className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl p-4 flex flex-col items-center justify-center opacity-70">
        <ShieldAlert className="h-8 w-8 text-[#666666] mb-2" />
        <span className="text-sm font-bold text-[#9A9A9A]">No active alerts assigned</span>
      </div>
    );
  }

  const getBorderColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return "border-red-500/50";
      case "HIGH": return "border-amber-500/50";
      case "MEDIUM": return "border-yellow-500/50";
      default: return "border-[#10B981]/50";
    }
  };

  return (
    <div className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-amber-500" /> Priority Alerts
        </h3>
        <span className="bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] px-2 py-0.5 rounded font-mono">
          {alerts.length} PENDING
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {alerts?.map((a) => (
          <div key={a.id} className={`bg-[#050505] p-3 rounded-lg border hover:bg-[#080808] transition-colors cursor-pointer ${getBorderColor(a.severity)}`}>
            <div className="flex items-center gap-2 mb-2">
              {a.severity === 'CRITICAL' ? <AlertTriangle className="h-3 w-3 text-red-500" /> : <ShieldAlert className="h-3 w-3 text-amber-500" />}
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#F5F5F5]">{a.type}</span>
            </div>
            <p className="text-xs font-medium text-white mb-2">{a.title}</p>
            <div className="flex justify-between items-center mt-2">
              <span className="text-[10px] px-1.5 py-0.5 bg-[#0D0D0D] text-[#9A9A9A] rounded uppercase">{a.district}</span>
              <span className="text-[10px] text-[#666666] font-mono">{new Date(a.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
