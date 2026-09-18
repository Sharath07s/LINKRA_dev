import React from "react";
import { ListOrdered } from "lucide-react";

export default function PriorityMatrix({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] animate-pulse"></div>;

  if (data.status === "insufficient_data") {
    return (
      <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col items-center justify-center">
        <div className="text-sm font-mono text-[#9A9A9A]">{data.message || "Insufficient Data"}</div>
      </div>
    );
  }

  const priorities = data.priorities || [];

  return (
    <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <ListOrdered className="h-4 w-4 text-orange-400" />
          Threat Prioritization
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {priorities?.map((p: any, i: number) => (
          <div key={i} className="flex items-center justify-between bg-black/40 p-2 rounded border border-[#222222]/50">
            <div className="flex items-center gap-3">
              <div className={`text-sm font-black ${p.priority_score > 75 ? 'text-red-400' : 'text-orange-400'}`}>
                #{i+1}
              </div>
              <div>
                <div className="text-xs font-bold text-white">{p.entity_type} {p.entity_id}</div>
                <div className="text-[10px] text-[#666666]">{p.explanation}</div>
              </div>
            </div>
            <div className="text-xs font-mono text-[#F5F5F5] bg-[#0D0D0D] px-2 py-1 rounded">
              {p.priority_score} PTS
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
