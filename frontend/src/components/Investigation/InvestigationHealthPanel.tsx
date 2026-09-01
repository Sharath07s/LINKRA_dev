"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Activity } from "lucide-react";

interface HealthProps {
  investigationId: string;
}

export default function InvestigationHealthPanel({ investigationId }: HealthProps) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await apiClient.get(`/investigations/${investigationId}/health`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch health score", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (investigationId) fetchHealth();
  }, [investigationId]);

  if (isLoading) return <div className="h-full flex items-center justify-center animate-pulse text-xs text-blue-400 font-bold uppercase tracking-widest">Calculating Metrics...</div>;
  if (!data) return null;

  const metrics = [
    { label: "Evidence", value: data.evidence_coverage },
    { label: "Suspects", value: data.suspect_coverage },
    { label: "Network", value: data.network_coverage },
    { label: "Timeline", value: data.timeline_coverage },
    { label: "Location", value: data.location_coverage },
  ];

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="h-4 w-4 text-emerald-500" />
        <h3 className="text-sm font-bold text-white tracking-wide">Investigation Health</h3>
      </div>
      
      <div className="flex items-center gap-6 mb-6">
        {/* Radial Progress representation */}
        <div className="relative w-16 h-16 shrink-0 flex items-center justify-center">
          <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="8" />
            <circle 
              cx="50" 
              cy="50" 
              r="45" 
              fill="none" 
              stroke="#10b981" 
              strokeWidth="8" 
              strokeDasharray="283" 
              strokeDashoffset={283 - (283 * data.overall_completeness) / 100}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <span className="text-sm font-black text-white">{data.overall_completeness}%</span>
          </div>
        </div>
        
        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Completeness Status</span>
          <span className="text-sm font-bold text-emerald-400 leading-tight block">Proceeding to Final Stages</span>
        </div>
      </div>

      <div className="space-y-3">
        {metrics?.map((m, idx) => (
          <div key={idx}>
            <div className="flex justify-between mb-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase">{m.label} Coverage</span>
              <span className="text-[10px] font-bold text-slate-300">{m.value}%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${m.value < 50 ? 'bg-amber-500' : 'bg-blue-500'}`} 
                style={{ width: `${m.value}%` }} 
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
