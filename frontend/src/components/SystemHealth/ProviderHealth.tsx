"use client";

import React from "react";
import { Cpu, XCircle, CheckCircle } from "lucide-react";

export default function ProviderHealth({ providers }: { providers: any[] }) {
  if (!providers) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Cpu className="h-4 w-4 text-[#10B981]" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">AI Providers</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {providers?.map((p, i) => (
          <div key={i} className="bg-[#050505] border border-[#222222] rounded p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              {p.status === "Healthy" ? (
                <CheckCircle className="h-3 w-3 text-emerald-500" />
              ) : (
                <XCircle className="h-3 w-3 text-red-500" />
              )}
              <div>
                <div className="text-xs font-bold text-[#F5F5F5]">{p.name}</div>
                <div className="text-[9px] text-[#666666] font-mono uppercase">{p.model}</div>
              </div>
            </div>
            <div className="flex flex-col items-end">
              <span className={`text-[10px] uppercase font-bold tracking-widest ${p.status === 'Healthy' ? 'text-emerald-500' : 'text-red-500'}`}>
                {p.status}
              </span>
              {p.status === "Healthy" && (
                <span className="text-[10px] font-mono text-[#9A9A9A]">{p.latency_ms}ms</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
