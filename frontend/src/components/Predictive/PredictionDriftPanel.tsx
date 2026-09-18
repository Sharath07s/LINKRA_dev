"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { GitPullRequestDraft } from "lucide-react";

export default function PredictionDriftPanel() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    apiClient.get("/model-monitoring/drift")
      .then(r => r.data)
      .then(res => setData(res))
      .catch(console.warn);
  }, []);

  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  if (data.status === "insufficient_data") {
    return (
      <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex items-center justify-center p-4 text-center">
        <p className="text-amber-500 text-[10px] font-mono">Insufficient temporal data to establish distribution baselines for drift detection.</p>
      </div>
    );
  }

  const volDrift = data.volume_drift_pct * 100;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <GitPullRequestDraft className="h-4 w-4 text-purple-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Distribution Drift</h3>
      </div>
      
      <div className="flex-1 p-4 space-y-3">
         <div className="flex justify-between items-center border-b border-[#222222] pb-2">
           <span className="text-[10px] text-[#9A9A9A] uppercase">Volume Drift</span>
           <span className={`text-xs font-mono font-bold ${Math.abs(volDrift) > 30 ? 'text-rose-500' : 'text-[#F5F5F5]'}`}>
             {volDrift > 0 ? '+' : ''}{volDrift.toFixed(1)}%
           </span>
         </div>
         <div className="flex justify-between items-center border-b border-[#222222] pb-2">
           <span className="text-[10px] text-[#9A9A9A] uppercase">Crime Type</span>
           <span className="text-xs font-mono text-emerald-500">{data.crime_type_drift}</span>
         </div>
         <div className="flex justify-between items-center border-b border-[#222222] pb-2">
           <span className="text-[10px] text-[#9A9A9A] uppercase">Spatial Shift</span>
           <span className="text-xs font-mono text-emerald-500">{data.spatial_distribution_drift}</span>
         </div>
         <div className="flex justify-between items-center">
           <span className="text-[10px] text-[#9A9A9A] uppercase">Graph Density</span>
           <span className="text-xs font-mono text-emerald-500">{data.network_structure_drift}</span>
         </div>
      </div>
    </div>
  );
}
