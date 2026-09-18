import React from "react";
import { Activity, AlertTriangle, Info } from "lucide-react";

export default function FusionOverview({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] animate-pulse"></div>;

  if (data.status === "insufficient_data") {
    return (
      <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col items-center justify-center text-center">
        <Info className="h-6 w-6 text-[#666666] mb-2" />
        <div className="text-sm font-mono text-[#9A9A9A]">Insufficient Historical Data</div>
        <div className="text-xs text-[#666666] mt-1">
          Required: {data.required_records} | Available: {data.available_records}
        </div>
      </div>
    );
  }

  const signals = data.signals || [];

  return (
    <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Activity className="h-4 w-4 text-emerald-400" />
          Fusion Signals
        </h3>
        <span className="text-[10px] font-mono px-2 py-1 rounded border bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
          {signals.length} ACTIVE
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {signals.length === 0 ? (
          <div className="text-xs font-mono text-[#666666] text-center py-4">No active signals</div>
        ) : (
          signals?.map((sig: any, i: number) => (
            <div key={i} className="bg-black/40 p-3 rounded-lg border border-[#222222]/50">
              <div className="flex justify-between items-start mb-2">
                <div className="text-sm font-bold text-white flex items-center gap-2">
                  {sig.risk_level === 'HIGH' && <AlertTriangle className="h-3 w-3 text-red-500" />}
                  {sig.signal}
                </div>
                <div className="text-xs font-mono text-emerald-400">CONF {sig.confidence}%</div>
              </div>
              <div className="text-[10px] text-[#9A9A9A] font-mono mb-2">
                SOURCES: {sig.source_systems?.join(" + ")}
              </div>
              <ul className="text-xs text-[#666666] space-y-1 list-disc pl-4">
                {sig.evidence?.map((ev: string, idx: number) => (
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
