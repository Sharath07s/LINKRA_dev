"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { ShieldAlert, Activity, AlertTriangle } from "lucide-react";

interface ThreatAssessmentProps {
  investigationId: string;
}

export default function ThreatAssessmentPanel({ investigationId }: ThreatAssessmentProps) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchThreat = async () => {
      try {
        const res = await apiClient.get(`/investigations/${investigationId}/threat-assessment`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch threat assessment", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (investigationId) fetchThreat();
  }, [investigationId]);

  if (isLoading) return <div className="h-full flex items-center justify-center animate-pulse text-xs text-red-400 font-bold uppercase tracking-widest">Assessing Threat...</div>;
  if (!data) return null;

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full">
      <div className="p-4 border-b border-slate-800 flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 text-red-500" />
        <h3 className="text-sm font-bold text-white tracking-wide">Threat Assessment</h3>
      </div>
      <div className="p-5 space-y-5 flex-1">
        
        <div className="flex items-end justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Threat Score</span>
            <div className="flex items-baseline gap-1">
              <span className="text-4xl font-black text-red-500 tracking-tighter">{data.threat_score}</span>
              <span className="text-sm text-slate-400 font-bold">/100</span>
            </div>
          </div>
          <div className="px-3 py-1 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] font-bold uppercase tracking-widest">
            {data.crime_severity} SEVERITY
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Network Influence</span>
              <span className="text-[10px] font-bold text-amber-400">{(data.network_influence * 100).toFixed(0)}%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full" style={{ width: `${data.network_influence * 100}%` }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Recidivism Risk</span>
              <span className="text-[10px] font-bold text-red-400">{(data.recidivism_score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-red-500 rounded-full" style={{ width: `${data.recidivism_score * 100}%` }} />
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800/50">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">Key Risk Factors</span>
          <div className="space-y-2">
            {data.risk_factors?.map((factor: string, idx: number) => (
              <div key={idx} className="flex items-center gap-2">
                <AlertTriangle className="h-3 w-3 text-amber-500 shrink-0" />
                <span className="text-xs font-medium text-slate-300">{factor}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
