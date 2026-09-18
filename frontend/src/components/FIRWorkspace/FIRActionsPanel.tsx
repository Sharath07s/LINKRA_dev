"use client";

import React from "react";
import { Download, FileText, Share2 } from "lucide-react";

export default function FIRActionsPanel() {
  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full justify-center">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4">
        <button className="flex items-center justify-center gap-2 p-3 bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 rounded-xl transition-colors text-indigo-400">
          <FileText className="h-4 w-4" />
          <span className="text-[10px] font-bold uppercase tracking-widest">Intelligence Brief</span>
        </button>
        <button className="flex items-center justify-center gap-2 p-3 bg-[#10B981]/15 hover:bg-[#10B981]/30 border border-[#10B981]/30 rounded-xl transition-colors text-[#10B981]">
          <Download className="h-4 w-4" />
          <span className="text-[10px] font-bold uppercase tracking-widest">PDF Export</span>
        </button>
        <button className="flex items-center justify-center gap-2 p-3 bg-[#0D0D0D]/50 hover:bg-[#111111]/50 border border-[#2A2A2A] rounded-xl transition-colors text-[#F5F5F5]">
          <Share2 className="h-4 w-4" />
          <span className="text-[10px] font-bold uppercase tracking-widest">Share Securely</span>
        </button>
      </div>
    </div>
  );
}
