"use client";

import React from "react";
import { Terminal } from "lucide-react";

export default function OfficerAuditTimeline({ logs }: { logs: any[] }) {
  return (
    <div suppressHydrationWarning className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Terminal className="h-4 w-4 text-emerald-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Audit Timeline</h3>
      </div>
      <div className="flex-1 overflow-y-auto p-3 bg-black/40">
        {(!logs || logs.length === 0) ? (
          <div className="text-center text-[#666666] text-xs font-mono py-4">No audit events generated.</div>
        ) : (
          <div className="space-y-1">
            {logs?.map((log: any) => (
              <div key={log.id} className="text-[10px] font-mono text-[#9A9A9A]">
                <span className="text-emerald-500">[{new Date(log.created_at).toISOString()}]</span> {log.action} - {log.resource_id || "SYSTEM"}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
