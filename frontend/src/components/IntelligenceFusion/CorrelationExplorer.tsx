import React from "react";
import { Link2, Network } from "lucide-react";

export default function CorrelationExplorer({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] animate-pulse"></div>;

  if (data.status === "insufficient_data") {
    return (
      <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col items-center justify-center">
        <div className="text-sm font-mono text-[#9A9A9A]">Insufficient Data for Correlation</div>
      </div>
    );
  }

  const correlations = data.correlations || [];

  return (
    <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Network className="h-4 w-4 text-indigo-400" />
          Correlation Engine
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {correlations.length === 0 ? (
          <div className="text-xs font-mono text-[#666666] text-center py-4">No significant correlations found</div>
        ) : (
          correlations?.map((corr: any, i: number) => (
            <div key={i} className="bg-indigo-500/5 p-3 rounded-lg border border-indigo-500/20">
              <div className="flex items-center gap-2 text-xs font-mono text-indigo-300 mb-2">
                <span>{corr.entity_a}</span>
                <Link2 className="h-3 w-3" />
                <span>{corr.entity_b}</span>
              </div>
              <div className="text-lg font-black text-white mb-1">Score: {corr.correlation_score}</div>
              <ul className="text-[10px] text-[#9A9A9A] list-disc pl-4 space-y-1">
                {corr.evidence?.map((ev: string, idx: number) => (
                  <li key={idx}>{ev}</li>
                ))}
              </ul>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
