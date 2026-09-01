"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Sparkles, BrainCircuit, Target, ShieldAlert, FileText } from "lucide-react";

interface AIFIRSummaryProps {
  firId: string;
}

export default function AIFIRSummary({ firId }: AIFIRSummaryProps) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await apiClient.get(`/crimes/${firId}/summary`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch FIR summary:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (firId) fetchSummary();
  }, [firId]);

  if (isLoading) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 rounded-2xl h-full p-5 flex flex-col items-center justify-center gap-3">
        <BrainCircuit className="h-8 w-8 text-purple-500 animate-pulse" />
        <span className="text-xs font-bold text-purple-400 uppercase tracking-widest animate-pulse">Generating Intelligence Summary...</span>
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
          <h3 className="text-sm font-bold text-white tracking-wide">AI Investigation Summary</h3>
        </div>
        <div className="px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[9px] font-bold uppercase tracking-widest">
          AI Generated
        </div>
      </div>
      
      <div className="p-5 flex-1 overflow-y-auto space-y-6">
        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2 flex items-center gap-1.5">
            <FileText className="h-3 w-3" /> Incident Summary
          </span>
          <p className="text-sm text-slate-200 leading-relaxed font-serif tracking-wide">
            {data.summary}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2 flex items-center gap-1.5">
              <Target className="h-3 w-3 text-blue-400" /> Modus Operandi & Pattern
            </span>
            <p className="text-xs text-slate-300 leading-relaxed">
              <span className="text-slate-100 font-semibold">{data.pattern}</span><br />
              {data.modus_operandi}
            </p>
          </div>
          <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2 flex items-center gap-1.5">
              <ShieldAlert className="h-3 w-3 text-red-400" /> Threat Assessment
            </span>
            <p className="text-xs text-slate-300 leading-relaxed">
              {data.threat_assessment}
            </p>
          </div>
        </div>

        <div>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-2">Recommended Actions</span>
          <div className="space-y-2">
            {data.recommended_actions?.map((action: string, idx: number) => (
              <div key={idx} className="flex items-center gap-2 p-2.5 bg-blue-950/10 border border-blue-900/20 rounded-lg">
                <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                <span className="text-xs font-medium text-blue-100">{action}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
