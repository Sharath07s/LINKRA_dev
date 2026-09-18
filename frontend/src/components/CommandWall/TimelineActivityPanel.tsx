"use client";

import React from "react";
import { Clock } from "lucide-react";

export default function TimelineActivityPanel({ timeline }: { timeline: any[] }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div suppressHydrationWarning className="h-full bg-[#080808] border border-[#222222] rounded-xl p-4 flex items-center justify-center">
        <span className="text-xs font-mono text-[#666666] uppercase tracking-widest">No Recent Activity</span>
      </div>
    );
  }

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Clock className="h-4 w-4 text-[#10B981]" /> Live Event Stream
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {timeline?.map((event, i) => (
          <div key={i} className="flex gap-3">
            <div className="flex flex-col items-center">
              <div className="h-2 w-2 rounded-full bg-blue-500 mt-1.5" />
              {i < timeline.length - 1 && <div className="w-px h-full bg-[#0D0D0D] my-1" />}
            </div>
            <div className="flex-1 pb-2">
              <span className="text-[10px] text-[#666666] font-mono">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
              <p className="text-xs text-[#F5F5F5] mt-0.5">{event.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
