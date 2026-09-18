"use client";

import React from "react";
import { Shield, Clock, Wifi } from "lucide-react";

export default function CommandWallHeader() {
  return (
    <div suppressHydrationWarning className="flex items-center justify-between p-4 bg-[#050505]/80 border-b border-[#222222]">
      <div className="flex items-center gap-4">
        <Shield className="h-8 w-8 text-[#10B981]" />
        <div>
          <h1 className="text-2xl font-black text-white tracking-widest uppercase">State Command Wall</h1>
          <p className="text-[10px] text-[#10B981] font-mono uppercase tracking-widest">Global Intelligence Sync Active</p>
        </div>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Wifi className="h-4 w-4 text-emerald-500 animate-pulse" />
          <span className="text-xs font-mono text-emerald-400 uppercase">Live Feed</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-[#9A9A9A]" />
          <span suppressHydrationWarning className="text-xs font-mono text-[#F5F5F5]">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}
