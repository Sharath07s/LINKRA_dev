"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { BrainCircuit } from "lucide-react";

export default function AIIntelligenceFeed() {
  const [feed, setFeed] = useState<any>(null);

  useEffect(() => {
    apiClient.post("/command-wall/intelligence-feed")
      .then(r => r.data)
      .then(d => setFeed(d))
      .catch(e => console.warn(e));
  }, []);

  if (!feed) {
    return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;
  }

  return (
    <div className="h-full bg-[#080808] border border-blue-900/40 rounded-xl flex flex-col overflow-hidden shadow-[0_0_15px_rgba(37,99,235,0.1)] relative">
      <div className="p-3 border-b border-[#10B981]/20 bg-blue-950/20 flex justify-between items-center">
        <h3 className="text-xs font-bold text-[#10B981] uppercase tracking-widest flex items-center gap-2">
          <BrainCircuit className="h-4 w-4 text-[#10B981]" /> State Intelligence Synthesis
        </h3>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
          CONFIDENCE: {feed.confidence}%
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 flex flex-col justify-center">
        {feed.findings?.map((f: string, i: number) => (
          <p key={i} className="text-lg font-serif text-[#F5F5F5] leading-relaxed border-l-4 border-[#10B981] pl-4">
            {f}
          </p>
        ))}
        
        {feed.evidence && feed.evidence.length > 0 && (
          <div className="mt-4 flex gap-2">
            {feed.evidence?.map((ev: string, i: number) => (
              <span key={i} className="text-[9px] font-mono bg-[#050505] text-[#666666] px-1.5 py-0.5 rounded border border-[#222222]">
                SOURCE: {ev}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
