"use client";

import React from "react";
import { CheckCircle, Database, Network, BrainCircuit, ShieldAlert } from "lucide-react";

interface AlertDetailsPanelProps {
  alert: any | null;
  onResolve: (id: string) => void;
}

export default function AlertDetailsPanel({ alert, onResolve }: AlertDetailsPanelProps) {
  if (!alert) {
    return (
      <div suppressHydrationWarning className="h-full flex flex-col items-center justify-center opacity-50 bg-[#080808]/40 border border-[#222222] rounded-2xl">
        <ShieldAlert className="h-10 w-10 text-[#666666] mb-3" />
        <span className="text-sm font-bold text-[#9A9A9A]">Select an alert to view intelligence details</span>
      </div>
    );
  }

  const getSourceIcon = (source: string) => {
    switch (source) {
      case "POSTGRESQL": return <Database className="h-3 w-3 text-emerald-400" />;
      case "NEO4J": return <Network className="h-3 w-3 text-purple-400" />;
      case "AI": return <BrainCircuit className="h-3 w-3 text-[#10B981]" />;
      default: return <Database className="h-3 w-3 text-[#9A9A9A]" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'CRITICAL': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'HIGH': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'MEDIUM': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      default: return 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20';
    }
  };

  return (
    <div className="h-full bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col overflow-hidden">
      <div className="p-5 border-b border-[#222222] bg-[#050505]/60">
        <div className="flex justify-between items-start mb-3">
          <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-widest border ${getSeverityColor(alert.severity)}`}>
            {alert.severity} PRIORITY
          </span>
          <span className="text-xs text-[#9A9A9A] font-mono">
            {new Date(alert.created_at).toLocaleString()}
          </span>
        </div>
        <h2 className="text-xl font-bold text-white mb-2">{alert.title}</h2>
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-bold text-[#F5F5F5] uppercase tracking-widest bg-[#0D0D0D] px-2 py-0.5 rounded flex items-center gap-1">
            {getSourceIcon(alert.source)} {alert.source} ENGINE
          </span>
          <span className="text-[10px] font-bold text-[#9A9A9A] uppercase tracking-widest">
            {alert.district}
          </span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        <div>
          <h4 className="text-xs font-bold text-[#666666] uppercase tracking-widest mb-2 border-b border-[#222222] pb-1">Intelligence Summary</h4>
          <p className="text-sm text-[#F5F5F5] leading-relaxed font-serif tracking-wide border-l-2 border-[#10B981] pl-3">
            {alert.description}
          </p>
        </div>

        {/* Dynamic Evidence block based on source */}
        <div>
           <h4 className="text-xs font-bold text-[#666666] uppercase tracking-widest mb-2 border-b border-[#222222] pb-1">Supporting Evidence</h4>
           <div className="bg-[#050505]/50 p-3 rounded-xl border border-[#222222] text-xs text-[#F5F5F5] font-mono">
             {alert.source === 'POSTGRESQL' && "> SQL Aggregation threshold breached. Volumetric analysis isolated anomaly."}
             {alert.source === 'NEO4J' && "> Cypher degree centrality constraint exceeded. Expanding network graph detected."}
           </div>
        </div>
      </div>

      <div className="p-4 border-t border-[#222222] bg-[#050505]/80 flex justify-end">
        <button 
          onClick={() => onResolve(alert.id)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600/20 border border-emerald-500/50 text-emerald-400 rounded-lg hover:bg-emerald-600/30 transition-colors text-xs font-bold uppercase tracking-wider"
        >
          <CheckCircle className="h-4 w-4" />
          Acknowledge & Resolve
        </button>
      </div>
    </div>
  );
}
