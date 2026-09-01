"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState } from "react";
import { UserPlus, Bell, FileText, Download, Network, Map as MapIcon, ShieldAlert } from "lucide-react";

interface ActionsPanelProps {
  investigationId: string;
}

export default function InvestigationActionsPanel({ investigationId }: ActionsPanelProps) {
  const [isAssigning, setIsAssigning] = useState(false);

  const handleAssign = async () => {
    setIsAssigning(true);
    try {
      await apiClient.post(`/investigations/${investigationId}/assign`);
      // Handle success locally
    } catch (e) {
      console.warn("Assignment failed", e);
    } finally {
      setIsAssigning(false);
    }
  };

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full">
      <div className="p-4 border-b border-slate-800 bg-slate-950/50">
        <h3 className="text-sm font-bold text-white tracking-wide">Command Actions</h3>
      </div>
      <div className="p-4 flex-1 grid grid-cols-2 gap-3">
        <button 
          onClick={handleAssign}
          disabled={isAssigning}
          className="flex flex-col items-center justify-center gap-2 p-3 bg-slate-950/60 hover:bg-slate-800 border border-slate-800 rounded-xl transition-colors group"
        >
          <UserPlus className="h-5 w-5 text-blue-400 group-hover:text-blue-300" />
          <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wide">Assign Officer</span>
        </button>
        
        <button className="flex flex-col items-center justify-center gap-2 p-3 bg-slate-950/60 hover:bg-slate-800 border border-slate-800 rounded-xl transition-colors group">
          <Bell className="h-5 w-5 text-amber-400 group-hover:text-amber-300" />
          <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wide">Create Alert</span>
        </button>
        
        <button className="flex flex-col items-center justify-center gap-2 p-3 bg-slate-950/60 hover:bg-slate-800 border border-slate-800 rounded-xl transition-colors group">
          <FileText className="h-5 w-5 text-emerald-400 group-hover:text-emerald-300" />
          <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wide">Generate Report</span>
        </button>
        
        <button className="flex flex-col items-center justify-center gap-2 p-3 bg-slate-950/60 hover:bg-slate-800 border border-slate-800 rounded-xl transition-colors group">
          <Download className="h-5 w-5 text-slate-400 group-hover:text-slate-300" />
          <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wide">Export PDF</span>
        </button>
      </div>
      <div className="p-4 border-t border-slate-800 bg-slate-950/30 flex gap-2">
        <button className="flex-1 py-2 bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 rounded-lg text-indigo-400 flex items-center justify-center gap-1.5 transition-colors">
          <Network className="h-4 w-4" />
          <span className="text-[10px] font-bold uppercase tracking-wider">Expand Graph</span>
        </button>
        <button className="flex-1 py-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 rounded-lg text-blue-400 flex items-center justify-center gap-1.5 transition-colors">
          <MapIcon className="h-4 w-4" />
          <span className="text-[10px] font-bold uppercase tracking-wider">Expand Map</span>
        </button>
      </div>
    </div>
  );
}
