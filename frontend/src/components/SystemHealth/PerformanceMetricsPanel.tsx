import React from "react";
import { Activity } from "lucide-react";

export default function PerformanceMetricsPanel({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] animate-pulse"></div>;

  return (
    <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Activity className="h-4 w-4 text-emerald-400" />
          Performance Metrics
        </h3>
      </div>

      {data.status === 'operational' ? (
        <div className="flex-1 grid grid-cols-2 gap-4">
          <div className="bg-black/40 p-3 rounded-lg border border-[#222222]/50 flex flex-col justify-center items-center">
            <div className="text-2xl font-mono text-emerald-400">{data.avg_api_latency_ms}ms</div>
            <div className="text-[10px] text-[#666666] font-mono mt-1">API LATENCY</div>
          </div>
          <div className="bg-black/40 p-3 rounded-lg border border-[#222222]/50 flex flex-col justify-center items-center">
            <div className="text-2xl font-mono text-[#10B981]">{data.recorded_requests}</div>
            <div className="text-[10px] text-[#666666] font-mono mt-1">TRAFFIC REQ</div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-[#666666] text-xs font-mono">
          Latency Metrics Unavailable
        </div>
      )}
    </div>
  );
}
