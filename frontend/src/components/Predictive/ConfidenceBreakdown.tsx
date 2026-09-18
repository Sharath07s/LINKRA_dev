import React from "react";
import { Activity } from "lucide-react";

interface ConfidenceBreakdownProps {
  score: number;
  level: "LOW" | "MEDIUM" | "HIGH" | "NONE";
}

export default function ConfidenceBreakdown({ score, level }: ConfidenceBreakdownProps) {
  let colorClass = "text-[#666666] bg-slate-500/10 border-slate-500/20";
  let barColorClass = "bg-slate-500";
  
  if (level === "HIGH") {
    colorClass = "text-emerald-500 bg-emerald-500/10 border-emerald-500/20";
    barColorClass = "bg-emerald-500";
  } else if (level === "MEDIUM") {
    colorClass = "text-amber-500 bg-amber-500/10 border-amber-500/20";
    barColorClass = "bg-amber-500";
  } else if (level === "LOW") {
    colorClass = "text-rose-500 bg-rose-500/10 border-rose-500/20";
    barColorClass = "bg-rose-500";
  }

  return (
    <div className="bg-[#050505] border border-[#222222] rounded p-3 mb-3">
      <div className="flex justify-between items-center mb-2">
        <h4 className="text-[10px] font-bold text-[#9A9A9A] uppercase tracking-widest flex items-center gap-1">
          <Activity className="h-3 w-3" /> Computed Confidence
        </h4>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${colorClass}`}>
          {level}
        </span>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="text-xl font-black text-white">{score}%</div>
        <div className="flex-1 h-1.5 bg-[#080808] rounded-full overflow-hidden">
          <div className={`h-full ${barColorClass}`} style={{ width: `${score}%` }}></div>
        </div>
      </div>
    </div>
  );
}
