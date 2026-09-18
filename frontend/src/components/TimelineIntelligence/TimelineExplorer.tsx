"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Search, ZoomIn, ZoomOut, Filter, ChevronRight, Activity, MapPin, ExternalLink, ShieldCheck } from "lucide-react";

interface TimelineExplorerProps {
  entityType: string;
  entityId: string;
}

export default function TimelineExplorer({ entityType, entityId }: TimelineExplorerProps) {
  const [events, setEvents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

  useEffect(() => {
    const fetchTimeline = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.get(`/timeline/?entity_type=${entityType}&entity_id=${entityId}`);
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
    fetchTimeline();
  }, [entityType, entityId]);

  const filteredEvents = events?.filter(e => 
    e.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    e.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div suppressHydrationWarning className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      {/* Toolbar */}
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex flex-col sm:flex-row justify-between items-center gap-3">
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#666666]" />
          <input 
            type="text" 
            placeholder="Search events..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#080808] border border-[#2A2A2A] rounded-lg pl-9 pr-4 py-1.5 text-sm text-[#F5F5F5] focus:outline-none focus:border-[#10B981]"
          />
        </div>
        <div className="flex items-center gap-2">
          <button className="p-1.5 rounded-lg bg-[#0D0D0D] text-[#9A9A9A] hover:text-[#F5F5F5] hover:bg-[#111111] transition-colors">
            <Filter className="h-4 w-4" />
          </button>
          <div className="h-4 w-px bg-[#111111] mx-1" />
          <button className="p-1.5 rounded-lg bg-[#0D0D0D] text-[#9A9A9A] hover:text-[#F5F5F5] hover:bg-[#111111] transition-colors">
            <ZoomOut className="h-4 w-4" />
          </button>
          <button className="p-1.5 rounded-lg bg-[#0D0D0D] text-[#9A9A9A] hover:text-[#F5F5F5] hover:bg-[#111111] transition-colors">
            <ZoomIn className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Explorer Body */}
      <div className="flex-1 p-6 overflow-y-auto relative bg-[#050505]/20">
        {isLoading ? (
          <div className="flex h-full items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <Activity className="h-6 w-6 text-[#10B981] animate-spin" />
              <span className="text-xs font-bold text-[#666666] uppercase tracking-widest">Compiling Chronology...</span>
            </div>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="flex h-full items-center justify-center flex-col gap-2">
            <ShieldCheck className="h-8 w-8 text-[#666666]" />
            <span className="text-sm text-[#9A9A9A] font-medium">No records found for this entity.</span>
          </div>
        ) : (
          <div className="space-y-6 relative before:absolute before:inset-0 before:ml-[28px] before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-blue-500/50 before:to-transparent">
            {filteredEvents?.map((event, idx) => {
              const isExpanded = expandedEventId === event.id;
              
              return (
                <div key={event.id || idx} className="relative flex items-start gap-5 group">
                  <div className="flex items-center justify-center w-[56px] h-[56px] rounded-xl border-2 border-[#222222] bg-[#080808] z-10 shadow-lg shadow-black/50 shrink-0 group-hover:border-[#10B981] group-hover:bg-blue-900/20 transition-colors">
                    <span suppressHydrationWarning className="text-[10px] font-bold text-[#9A9A9A] group-hover:text-[#10B981]">
                      {new Date(event.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  
                  <div suppressHydrationWarning 
                    onClick={() => setExpandedEventId(isExpanded ? null : event.id)}
                    className={`flex-1 rounded-xl border transition-all cursor-pointer overflow-hidden ${
                      isExpanded ? "border-[#10B981]/50 bg-[#080808]/80 shadow-lg shadow-blue-900/20" : "border-[#222222] bg-[#050505]/60 hover:border-[#2A2A2A]"
                    }`}
                  >
                    <div className="p-4 flex justify-between items-center">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold text-[#10B981] uppercase tracking-widest bg-[#10B981]/10 px-2 py-0.5 rounded border border-[#10B981]/20">
                            {event.type}
                          </span>
                          <span suppressHydrationWarning className="text-[10px] text-[#666666] font-mono">
                            {new Date(event.date).toLocaleTimeString()}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-white">{event.title}</h4>
                      </div>
                      <ChevronRight className={`h-5 w-5 text-[#666666] transition-transform ${isExpanded ? "rotate-90 text-[#10B981]" : ""}`} />
                    </div>

                    {isExpanded && (
                      <div className="p-4 border-t border-[#222222] bg-[#050505]/50 space-y-4">
                        <p className="text-xs text-[#F5F5F5] leading-relaxed">
                          {event.description}
                        </p>
                        
                        <div className="flex gap-2">
                          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider hover:bg-emerald-500/20 transition-colors">
                            <MapPin className="h-3 w-3" /> Map Context
                          </button>
                          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-bold uppercase tracking-wider hover:bg-purple-500/20 transition-colors">
                            <ExternalLink className="h-3 w-3" /> Neo4j Node
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
