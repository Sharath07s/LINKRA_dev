"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Sparkles, BrainCircuit, CheckCircle2, Crosshair, AlertTriangle } from "lucide-react";

export default function AIExecutiveBriefing() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBriefing = async () => {
      try {
        const res = await apiClient.post(`/executive/briefing`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch briefing:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchBriefing();
  }, []);

  if (isLoading) {
    return (
      <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl h-full p-5 flex flex-col items-center justify-center gap-3">
        <BrainCircuit className="h-8 w-8 text-[#10B981] animate-pulse" />
        <span className="text-xs font-bold text-[#10B981] uppercase tracking-widest animate-pulse">Compiling Executive Briefing...</span>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl h-full flex flex-col overflow-hidden relative">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500" />
      
      <div className="p-5 border-b border-[#222222] bg-[#050505]/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-[#10B981]" />
          <h3 className="text-base font-bold text-white tracking-wide">AI Executive Intelligence Brief</h3>
        </div>
        <div className="flex flex-col items-end">
          <div className="px-2 py-0.5 rounded bg-[#10B981]/10 border border-[#10B981]/20 text-[#10B981] text-[9px] font-bold uppercase tracking-widest mb-1">
            Real-time RAG Synthesis
          </div>
          <span className="text-[10px] text-[#666666] font-mono font-bold">Conf: {data.confidence}%</span>
        </div>
      </div>
      
      <div className="p-6 flex-1 overflow-y-auto space-y-6">
        <div>
          <span className="text-[10px] font-bold text-[#666666] uppercase tracking-widest block mb-2">Strategic Assessment</span>
          <p className="text-sm md:text-base text-[#F5F5F5] leading-relaxed font-serif tracking-wide border-l-2 border-[#10B981] pl-4 py-1">
            {data.summary}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-[#050505]/60 border border-[#222222] p-4 rounded-xl">
            <span className="text-[10px] font-bold text-[#666666] uppercase tracking-widest block mb-3 flex items-center gap-1.5">
              <AlertTriangle className="h-3 w-3 text-red-400" /> Key Risks Identified
            </span>
            <ul className="space-y-3">
              {data.key_risks?.map((risk: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-[#F5F5F5] leading-relaxed">
                  <div className="h-1.5 w-1.5 rounded-full bg-red-500 mt-1.5 shrink-0" />
                  {risk}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="bg-[#050505]/60 border border-[#222222] p-4 rounded-xl">
            <span className="text-[10px] font-bold text-[#666666] uppercase tracking-widest block mb-3 flex items-center gap-1.5">
              <Crosshair className="h-3 w-3 text-emerald-400" /> Recommended Actions
            </span>
            <ul className="space-y-3">
              {data.recommended_actions?.map((action: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-[#F5F5F5] leading-relaxed">
                  <CheckCircle2 className="h-3 w-3 text-emerald-500 mt-0.5 shrink-0" />
                  {action}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="pt-4 border-t border-[#222222] flex flex-wrap items-center gap-2">
          <span className="text-[10px] font-bold text-[#666666] uppercase tracking-widest mr-2">Evidence Sources:</span>
          {data.evidence_sources?.map((src: string, idx: number) => (
            <span key={idx} className="px-2 py-1 rounded-md bg-[#0D0D0D] border border-[#2A2A2A] text-[9px] text-[#9A9A9A] font-mono">
              {src}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
