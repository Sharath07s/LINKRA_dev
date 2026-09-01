import { apiClient } from "@/lib/api-client";
import React, { useState } from "react";
import { MessageSquare, Bot } from "lucide-react";

export default function FusionBriefingPanel({ data }: { data: any }) {
  const [briefing, setBriefing] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!data) return <div className="h-full bg-slate-900/50 rounded-xl border border-slate-800 animate-pulse"></div>;

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post("/fusion/briefing");
      const result = response.data;
      setBriefing(result.briefing);
    } catch (e) {
      setBriefing("Failed to generate briefing. Ensure backend is running.");
    }
    setLoading(false);
  };

  return (
    <div className="h-full bg-slate-900/50 rounded-xl border border-slate-800 p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-cyan-400" />
          AI Commander Briefing
        </h3>
        <button 
          onClick={handleGenerate} 
          disabled={loading || data.status === "insufficient_data"}
          className="flex items-center gap-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-[10px] px-3 py-1 rounded transition-colors disabled:opacity-50"
        >
          <Bot className="h-3 w-3" />
          {loading ? "GENERATING..." : "REQUEST BRIEFING"}
        </button>
      </div>

      <div className="flex-1 bg-black/40 rounded-lg border border-slate-800/50 p-4 overflow-y-auto">
        {briefing ? (
          <p className="text-sm text-slate-300 leading-relaxed font-mono whitespace-pre-wrap">{briefing}</p>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <Bot className="h-8 w-8 mb-2 opacity-50" />
            <p className="text-xs font-mono">Awaiting Commander Request</p>
            <p className="text-[10px] mt-2 max-w-xs text-center">Generates a situational report constrained exclusively to real, validated intelligence signals.</p>
          </div>
        )}
      </div>
    </div>
  );
}
