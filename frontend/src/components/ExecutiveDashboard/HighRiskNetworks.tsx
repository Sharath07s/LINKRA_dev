"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Network } from "lucide-react";

export default function HighRiskNetworks() {
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchNetworks = async () => {
      try {
        const res = await apiClient.get(`/executive/high-risk-networks`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch high risk networks:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchNetworks();
  }, []);

  if (isLoading) return <div className="h-full bg-slate-900/40 border border-slate-800 rounded-2xl animate-pulse"></div>;

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-slate-800 bg-slate-950/50 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Network className="h-4 w-4 text-purple-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">High Risk Networks</h3>
        </div>
        <span className="text-[9px] bg-purple-900/30 text-purple-400 border border-purple-800/50 px-2 py-0.5 rounded font-mono uppercase">
          Neo4j PageRank
        </span>
      </div>
      
      <div className="flex-1 overflow-x-auto p-4 space-y-3">
        {data?.map((network, idx) => (
          <div key={idx} className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl hover:border-purple-500/50 transition-colors">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-bold text-white">{network.name}</h4>
              <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${network.risk_score >= 90 ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                {network.risk_score}
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-2 mt-3">
              <div className="flex flex-col">
                <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Members</span>
                <span className="text-sm font-bold text-slate-200">{network.members}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Crimes</span>
                <span className="text-sm font-bold text-slate-200">{network.crimes}</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Districts</span>
                <span className="text-xs font-medium text-slate-300 leading-tight">{network.districts.join(", ")}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
