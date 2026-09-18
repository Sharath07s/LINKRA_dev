"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { Share2, AlertTriangle, Network } from "lucide-react";

export default function NetworkGrowth() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/predictive/networks")
      .then(r => r.data)
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const isInsufficient = data?.status === "insufficient_data";

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Share2 className="h-4 w-4 text-purple-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Syndicate Expansion Risk</h3>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto relative">
        {isInsufficient ? (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-50" />
            <h4 className="text-sm font-bold text-amber-500 mb-1">Insufficient Graph Data</h4>
            <p className="text-xs text-[#9A9A9A] font-mono mb-2">{data.message}</p>
            <div className="inline-flex items-center gap-2 text-[10px] bg-[#050505] px-2 py-1 rounded border border-[#222222]">
              <span className="text-[#666666]">Required: {data.required_records}</span>
              <span className="text-[#666666]">|</span>
              <span className="text-amber-500">Available: {data.available_records}</span>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {data?.network_predictions?.map((net: any, i: number) => (
              <div key={i} className="bg-[#050505] border border-purple-500/20 rounded p-3">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    <Network className="h-3 w-3 text-purple-500" />
                    <span className="text-xs font-bold text-white">{net.suspect_name}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${net.expansion_risk === 'HIGH' ? 'text-rose-500 border-rose-500/20 bg-rose-500/10' : 'text-amber-500 border-amber-500/20 bg-amber-500/10'}`}>
                    {net.expansion_risk} RISK
                  </span>
                </div>
                <div className="flex justify-between text-[10px] text-[#9A9A9A] font-mono">
                  <span>Current Degree: {net.current_degree}</span>
                  <span className="text-purple-400">Predicted +{net.predicted_new_connections_30d} (30d)</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
