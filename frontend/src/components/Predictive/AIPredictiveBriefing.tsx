"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, FileText, AlertTriangle } from "lucide-react";
import { apiClient } from "@/lib/api-client";

export default function AIPredictiveBriefing() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.post("/predictive/briefing")
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const briefing = data?.briefing;
  const isError = data?.status === "error";

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden relative">
      <div className="p-4 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-[#10B981]" /> AI Executive Predictive Briefing
        </h3>
        <span className="text-[10px] text-[#666666] font-mono border border-[#2A2A2A] rounded px-2">AUTO-GENERATED</span>
      </div>
      
      <div className="flex-1 p-6 overflow-y-auto text-sm text-[#F5F5F5] space-y-6">
        {isError || !briefing ? (
           <div className="h-full flex flex-col justify-center items-center text-center">
             <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-50" />
             <h4 className="text-sm font-bold text-amber-500 mb-1">Briefing Generation Failed</h4>
             <p className="text-xs text-[#9A9A9A] font-mono mb-2">{data?.message || "Check LLM Provider connectivity."}</p>
           </div>
        ) : (
          <>
            <div>
              <h4 className="text-xs font-bold text-[#666666] uppercase tracking-widest mb-2 flex items-center gap-2"><FileText className="h-3 w-3"/> Executive Summary</h4>
              <p className="leading-relaxed">{briefing.executive_summary}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h4 className="text-xs font-bold text-rose-500 uppercase tracking-widest mb-2">Key Forecasted Risks</h4>
                <ul className="list-disc pl-4 space-y-2 text-[#9A9A9A]">
                  {briefing.key_risks?.map((risk: string, i: number) => <li key={i}>{risk}</li>)}
                </ul>
              </div>
              <div>
                <h4 className="text-xs font-bold text-emerald-500 uppercase tracking-widest mb-2">Recommended Preventive Actions</h4>
                <ul className="list-disc pl-4 space-y-2 text-[#9A9A9A]">
                  {briefing.recommended_actions?.map((act: string, i: number) => <li key={i}>{act}</li>)}
                </ul>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-[#222222] bg-[#050505]/30 p-3 rounded">
              <span className="block text-[10px] font-bold text-[#666666] uppercase tracking-widest mb-2">Grounding Evidence</span>
              <ul className="text-[10px] font-mono text-[#9A9A9A] space-y-1">
                {data.evidence?.map((ev: string, i: number) => <li key={i}>• {ev}</li>)}
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
