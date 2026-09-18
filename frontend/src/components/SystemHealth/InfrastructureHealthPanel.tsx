import React from "react";
import { Server, Cpu, HardDrive } from "lucide-react";

export default function InfrastructureHealthPanel({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] animate-pulse"></div>;

  return (
    <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Server className="h-4 w-4 text-purple-400" />
          Infrastructure Health
        </h3>
        <span className={`text-[10px] font-mono px-2 py-1 rounded border ${data.status === 'operational' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'}`}>
          {data.status === 'operational' ? 'ONLINE' : 'UNAVAILABLE'}
        </span>
      </div>

      {data.status === 'operational' ? (
        <div className="flex-1 grid grid-cols-2 gap-4">
          <div className="bg-black/40 p-3 rounded-lg border border-[#222222]/50">
            <div className="text-xs text-[#666666] font-mono mb-1 flex items-center gap-1"><Cpu className="h-3 w-3"/> CPU Usage</div>
            <div className="text-xl font-mono text-emerald-400">{data.cpu_usage_percent}%</div>
          </div>
          <div className="bg-black/40 p-3 rounded-lg border border-[#222222]/50">
            <div className="text-xs text-[#666666] font-mono mb-1 flex items-center gap-1"><HardDrive className="h-3 w-3"/> Memory Usage</div>
            <div className="text-xl font-mono text-emerald-400">{data.memory_usage_percent}%</div>
            <div className="text-[10px] text-[#666666]">{data.memory_used_gb} / {data.memory_total_gb} GB</div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-[#666666] text-xs font-mono">
          Metrics Unavailable
        </div>
      )}
    </div>
  );
}
