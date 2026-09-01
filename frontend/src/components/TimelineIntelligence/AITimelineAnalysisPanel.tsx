"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Sparkles, BrainCircuit, Activity, TrendingUp, AlertTriangle } from "lucide-react";

interface AITimelineAnalysisProps {
  entityType: string;
  entityId: string;
}

export default function AITimelineAnalysisPanel({ entityType, entityId }: AITimelineAnalysisProps) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.get(`/timeline/analysis?entity_type=${entityType}&entity_id=${entityId}`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch timeline analysis:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalysis();
  }, [entityType, entityId]);

  if (isLoading) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 rounded-2xl h-full p-5 flex flex-col items-center justify-center gap-3">
        <BrainCircuit className="h-8 w-8 text-purple-500 animate-pulse" />
        <span className="text-xs font-bold text-purple-400 uppercase tracking-widest animate-pulse">Analyzing Chronology...</span>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl h-full flex flex-col overflow-hidden relative">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-blue-500 to-emerald-500" />
      
      <div className="p-4 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-purple-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">AI Timeline Intelligence</h3>
        </div>
        <div className="px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[9px] font-bold uppercase tracking-widest">
          {data.provider}
        </div>
      </div>
      
      <div className="p-5 flex-1 overflow-y-auto space-y-5">
        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">Chronological Synthesis</span>
          <p className="text-sm text-slate-200 leading-relaxed font-serif">
            {data.insights}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-3">
          <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex items-start gap-3">
            <Activity className="h-4 w-4 text-emerald-400 mt-0.5" />
            <div>
              <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest block mb-1">Behavioral Changes</span>
              <p className="text-xs text-slate-300">{data.behavioral_changes}</p>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex items-start gap-3">
            <TrendingUp className="h-4 w-4 text-amber-400 mt-0.5" />
            <div>
              <span className="text-[10px] font-bold text-amber-400 uppercase tracking-widest block mb-1">Escalation Patterns</span>
              <p className="text-xs text-slate-300">{data.escalation_patterns}</p>
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex items-start gap-3">
            <AlertTriangle className="h-4 w-4 text-red-400 mt-0.5" />
            <div>
              <span className="text-[10px] font-bold text-red-400 uppercase tracking-widest block mb-1">Recidivism / Repeat Offender</span>
              <p className="text-xs text-slate-300">{data.repeat_offender_indicators}</p>
            </div>
          </div>
        </div>

        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">Key Extracted Events</span>
          <ul className="space-y-2">
            {data.key_events?.map((evt: string, idx: number) => (
              <li key={idx} className="flex items-center gap-2 text-xs text-slate-300">
                <div className="h-1.5 w-1.5 rounded-full bg-blue-500" /> {evt}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
