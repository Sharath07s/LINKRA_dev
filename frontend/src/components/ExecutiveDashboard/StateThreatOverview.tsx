"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, Activity } from "lucide-react";

export default function StateThreatOverview() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchThreatLevel = async () => {
      try {
        const res = await apiClient.get(`/executive/threat-level`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch state threat level", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchThreatLevel();
  }, []);

  if (isLoading) return <div className="h-full bg-slate-900/40 border border-slate-800 rounded-2xl animate-pulse"></div>;
  if (!data) return null;

  const getLevelColor = (level: string) => {
    switch(level) {
      case 'CRITICAL': return 'text-red-500 bg-red-500/10 border-red-500/30 shadow-red-500/20';
      case 'HIGH': return 'text-amber-500 bg-amber-500/10 border-amber-500/30 shadow-amber-500/20';
      case 'MEDIUM': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30 shadow-yellow-500/20';
      default: return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30 shadow-emerald-500/20';
    }
  };

  return (
    <div className={`border rounded-2xl h-full flex flex-col justify-center relative overflow-hidden transition-all duration-500 ${getLevelColor(data.level)} shadow-[inset_0_0_50px_rgba(0,0,0,0.5)]`}>
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />
      
      <div className="relative z-10 flex flex-col md:flex-row items-center justify-between p-6 md:p-8 gap-6">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="absolute inset-0 rounded-full animate-ping opacity-20 bg-current"></div>
            <div className="h-16 w-16 rounded-full border-2 border-current bg-slate-950 flex items-center justify-center relative z-10">
              <AlertTriangle className="h-8 w-8" />
            </div>
          </div>
          <div>
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-300 mb-1">Strategic Threat Level</h2>
            <div className="flex items-end gap-3">
              <span className="text-4xl md:text-5xl font-bold tracking-tighter leading-none">{data.level}</span>
              <span className="text-xl font-bold mb-1 opacity-80">({data.score}/100)</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-2 w-full md:w-auto">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-current/20 pb-1 mb-1">Driving Factors</span>
          {data.factors?.map((factor: any, idx: number) => (
            <div key={idx} className="flex justify-between items-center gap-6 text-xs font-medium">
              <span className="text-slate-200 flex items-center gap-1.5"><Activity className="h-3 w-3" /> {factor.name}</span>
              <span className="uppercase tracking-widest text-[10px] opacity-80">{factor.impact}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
