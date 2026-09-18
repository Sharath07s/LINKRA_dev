"use client";

import React from "react";
import { AlertTriangle, ShieldAlert, AlertCircle, Info } from "lucide-react";

export default function ThreatLevelPanel({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  let config = { color: "text-[#10B981]", bg: "bg-[#10B981]/10", border: "border-[#10B981]/30", icon: <Info className="h-8 w-8 text-[#10B981]" /> };
  
  switch (data.level) {
    case "CRITICAL": config = { color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/30", icon: <AlertTriangle className="h-8 w-8 text-red-500" /> }; break;
    case "HIGH": config = { color: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/30", icon: <ShieldAlert className="h-8 w-8 text-amber-500" /> }; break;
    case "MEDIUM": config = { color: "text-yellow-500", bg: "bg-yellow-500/10", border: "border-yellow-500/30", icon: <AlertCircle className="h-8 w-8 text-yellow-500" /> }; break;
  }

  return (
    <div className={`h-full ${config.bg} border ${config.border} rounded-xl p-4 flex flex-col justify-center items-center relative overflow-hidden`}>
      <h3 className="text-xs font-bold text-[#9A9A9A] uppercase tracking-widest absolute top-3 left-3">State Threat Level</h3>
      
      <div className="flex flex-col items-center gap-2 mt-4">
        {config.icon}
        <span className={`text-4xl font-black tracking-widest uppercase ${config.color}`}>{data.level}</span>
        <span className="text-xs font-mono text-[#9A9A9A]">Score: {data.score}/100</span>
      </div>
      
      <div className="mt-4 flex gap-2 flex-wrap justify-center">
        {data.factors?.map((f: string, i: number) => (
          <span key={i} className="text-[9px] bg-[#050505] text-[#F5F5F5] px-2 py-1 rounded font-mono border border-[#222222]">
            {f}
          </span>
        ))}
      </div>
    </div>
  );
}
