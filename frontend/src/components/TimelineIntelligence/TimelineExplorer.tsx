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
    <div suppressHydrationWarning className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full overflow-hidden">
      {/* Toolbar */}
      <div className="p-3 border-b border-slate-800 bg-slate-950/50 flex flex-col sm:flex-row justify-between items-center gap-3">
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search events..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <button className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors">
            <Filter className="h-4 w-4" />
          </button>
          <div className="h-4 w-px bg-slate-700 mx-1" />
          <button className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors">
            <ZoomOut className="h-4 w-4" />
          </button>
          <button className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors">
            <ZoomIn className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Explorer Body */}
      <div className="flex-1 p-6 overflow-y-auto relative bg-slate-950/20">
        {isLoading ? (
          <div className="flex h-full items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <Activity className="h-6 w-6 text-blue-500 animate-spin" />
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Compiling Chronology...</span>
            </div>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="flex h-full items-center justify-center flex-col gap-2">
            <ShieldCheck className="h-8 w-8 text-slate-600" />
            <span className="text-sm text-slate-400 font-medium">No records found for this entity.</span>
          </div>
        ) : (
          <div className="space-y-6 relative before:absolute before:inset-0 before:ml-[28px] before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-blue-500/50 before:to-transparent">
            {filteredEvents?.map((event, idx) => {
              const isExpanded = expandedEventId === event.id;
              
              return (
                <div key={event.id || idx} className="relative flex items-start gap-5 group">
                  <div className="flex items-center justify-center w-[56px] h-[56px] rounded-xl border-2 border-slate-800 bg-slate-900 z-10 shadow-lg shadow-black/50 shrink-0 group-hover:border-blue-500 group-hover:bg-blue-900/20 transition-colors">
                    <span suppressHydrationWarning className="text-[10px] font-bold text-slate-400 group-hover:text-blue-300">
                      {new Date(event.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  
                  <div suppressHydrationWarning 
                    onClick={() => setExpandedEventId(isExpanded ? null : event.id)}
                    className={`flex-1 rounded-xl border transition-all cursor-pointer overflow-hidden ${
                      isExpanded ? "border-blue-500/50 bg-slate-900/80 shadow-lg shadow-blue-900/20" : "border-slate-800 bg-slate-950/60 hover:border-slate-700"
                    }`}
                  >
                    <div className="p-4 flex justify-between items-center">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                            {event.type}
                          </span>
                          <span suppressHydrationWarning className="text-[10px] text-slate-500 font-mono">
                            {new Date(event.date).toLocaleTimeString()}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-white">{event.title}</h4>
                      </div>
                      <ChevronRight className={`h-5 w-5 text-slate-500 transition-transform ${isExpanded ? "rotate-90 text-blue-400" : ""}`} />
                    </div>

                    {isExpanded && (
                      <div className="p-4 border-t border-slate-800 bg-slate-950/50 space-y-4">
                        <p className="text-xs text-slate-300 leading-relaxed">
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
