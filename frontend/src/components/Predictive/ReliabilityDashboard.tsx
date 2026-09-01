"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { ShieldCheck } from "lucide-react";

export default function ReliabilityDashboard() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    apiClient.get("/model-monitoring/summary")
      .then(r => r.data)
      .then(res => setData(res))
      .catch(console.warn);
  }, []);

  if (!data) return <div className="h-full bg-slate-900 border border-slate-800 rounded-xl animate-pulse"></div>;

  if (data.status === "insufficient_data") {
    return null;
  }

  const score = data.reliability_score;
  const level = data.reliability_level;

  let color = "text-emerald-500";
  if (level === "MEDIUM") color = "text-amber-500";
  if (level === "LOW") color = "text-rose-500";

  return (
    <div className="h-full bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800 bg-slate-950/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
           <ShieldCheck className="h-4 w-4 text-blue-500" />
           <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Confidence Reliability</h3>
        </div>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${color} bg-opacity-10 border-opacity-20`}>
           {level}
        </span>
      </div>
      
      <div className="flex-1 p-4 flex flex-col justify-center items-center">
         <div className={`text-4xl font-black ${color}`}>{score}/100</div>
         <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-2 text-center">
           Correlation between system confidence and historical outcomes
         </p>
      </div>
    </div>
  );
}
