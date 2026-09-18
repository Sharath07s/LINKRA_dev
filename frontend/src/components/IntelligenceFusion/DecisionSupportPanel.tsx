import React from "react";
import { ShieldAlert, Crosshair } from "lucide-react";

export default function DecisionSupportPanel({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] animate-pulse"></div>;

  if (data.status === "insufficient_data") {
    return (
      <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col items-center justify-center">
        <div className="text-sm font-mono text-[#9A9A9A]">No Actionable Recommendations</div>
      </div>
    );
  }

  const recommendations = data.recommendations || [];

  return (
    <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-rose-400" />
          Autonomous Decision Support
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {recommendations.length === 0 ? (
          <div className="text-xs font-mono text-[#666666] text-center py-4">System nominal. No escalated decisions required.</div>
        ) : (
          recommendations?.map((rec: any, i: number) => (
            <div key={i} className="bg-rose-500/10 p-4 rounded-lg border border-rose-500/30">
              <div className="flex items-center gap-2 text-rose-400 mb-2 font-bold uppercase tracking-wide text-sm">
                <Crosshair className="h-4 w-4" />
                {rec.action}
              </div>
              <div className="text-xs text-white mb-2">{rec.justification}</div>
              <div className="text-[10px] text-[#9A9A9A] font-mono">CONF: {rec.confidence}% | SOURCES: {rec.source_systems.join(", ")}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
