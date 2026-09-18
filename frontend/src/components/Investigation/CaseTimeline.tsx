"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Clock, Activity, FileText, Filter, Search, ChevronRight } from "lucide-react";

interface TimelineEvent {
  id: string;
  type: string;
  date: string;
  title: string;
  description: string;
  entity_type: string;
}

interface CaseTimelineProps {
  investigationId: string;
}

export default function CaseTimeline({ investigationId }: CaseTimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTimeline = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.get(`/investigations/${investigationId}/timeline`);
        if (res.status === 200) {
          const data = res.data;
          setEvents(data);
        }
      } catch (err) {
        console.warn("Failed to fetch timeline:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (investigationId) {
      fetchTimeline();
    }
  }, [investigationId]);

  return (
    <div suppressHydrationWarning className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-[#222222] flex justify-between items-center bg-[#050505]/50">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-emerald-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">Investigation Timeline</h3>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-1.5 rounded-lg bg-[#080808] border border-[#222222] text-[#9A9A9A] hover:text-white transition-colors">
            <Search className="h-3.5 w-3.5" />
          </button>
          <button className="p-1.5 rounded-lg bg-[#080808] border border-[#222222] text-[#9A9A9A] hover:text-white transition-colors">
            <Filter className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <div className="p-5 flex-1 overflow-y-auto relative">
        {isLoading ? (
          <div className="flex h-full items-center justify-center">
            <span className="text-xs text-emerald-400 font-bold tracking-widest uppercase animate-pulse">Loading Chronology...</span>
          </div>
        ) : events.length === 0 ? (
          <div className="flex h-full items-center justify-center flex-col gap-2">
            <Activity className="h-6 w-6 text-[#666666]" />
            <span className="text-xs text-[#666666] font-medium">No chronological events found</span>
          </div>
        ) : (
          <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-slate-800 before:to-transparent">
            {events?.map((event, idx) => (
              <div key={event.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                {/* Timeline Marker */}
                <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-slate-900 bg-[#0D0D0D] text-[#9A9A9A] shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 group-hover:bg-emerald-500/20 group-hover:border-emerald-500/30 group-hover:text-emerald-400 transition-colors">
                  <FileText className="h-4 w-4" />
                </div>
                
                {/* Event Card */}
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-[#222222] bg-[#050505]/60 shadow-sm group-hover:border-[#2A2A2A] transition-colors cursor-pointer relative">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">{event.entity_type}</span>
                    </div>
                    <time className="text-[10px] text-[#666666] font-mono">
                      {new Date(event.date).toLocaleString()}
                    </time>
                  </div>
                  <h4 className="text-sm font-bold text-white mb-1.5">{event.title}</h4>
                  <p className="text-xs text-[#9A9A9A] line-clamp-2">{event.description}</p>
                  <div className="mt-2 pt-2 border-t border-[#222222]/50 flex justify-end">
                    <span className="text-[10px] font-semibold text-[#10B981] flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                      Expand Details <ChevronRight className="h-3 w-3 ml-0.5" />
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
