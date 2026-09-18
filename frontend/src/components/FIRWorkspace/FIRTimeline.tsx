"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Clock, Activity, FileText } from "lucide-react";

interface FIRTimelineProps {
  firId: string;
}

export default function FIRTimeline({ firId }: FIRTimelineProps) {
  const [events, setEvents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await apiClient.get(`/crimes/${firId}/timeline`);
        if (res.status === 200) {
          const data = res.data;
          setEvents(data);
        }
      } catch (err) {
        console.warn("Failed to fetch FIR timeline:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (firId) fetchTimeline();
  }, [firId]);

  return (
    <div suppressHydrationWarning className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Clock className="h-4 w-4 text-[#9A9A9A]" />
        <h3 className="text-sm font-bold text-white tracking-wide">Incident Chronology</h3>
      </div>

      <div className="p-5 flex-1 overflow-y-auto relative">
        {isLoading ? (
          <div className="flex h-full items-center justify-center">
            <span className="text-xs text-[#666666] font-bold tracking-widest uppercase animate-pulse">Loading Chronology...</span>
          </div>
        ) : events.length === 0 ? (
          <div className="flex h-full items-center justify-center flex-col gap-2">
            <Activity className="h-6 w-6 text-[#666666]" />
            <span className="text-xs text-[#666666] font-medium">No chronological events found</span>
          </div>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-slate-800 before:to-transparent">
            {events?.map((event, idx) => (
              <div key={event.id || idx} className="relative flex items-start gap-4 group">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-slate-900 bg-[#0D0D0D] text-[#9A9A9A] shrink-0 z-10 group-hover:bg-[#10B981]/15 group-hover:border-[#10B981]/30 group-hover:text-[#10B981] transition-colors">
                  <FileText className="h-4 w-4" />
                </div>
                
                <div className="flex-1 p-3 rounded-xl border border-[#222222] bg-[#050505]/60 group-hover:border-[#2A2A2A] transition-colors mt-1">
                  <div className="flex justify-between items-baseline mb-1">
                    <span className="text-[10px] font-bold text-[#10B981] uppercase tracking-wider">{event.type}</span>
                    <time className="text-[9px] text-[#666666] font-mono">
                      {new Date(event.date).toLocaleString()}
                    </time>
                  </div>
                  <h4 className="text-xs font-bold text-white mb-1">{event.title}</h4>
                  <p className="text-[11px] text-[#9A9A9A] leading-relaxed">{event.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
