"use client";

import React from "react";
import { User, Shield, Radio, Activity } from "lucide-react";

interface OfficerHeaderProps {
  user: any;
}

export default function OfficerHeader({ user }: OfficerHeaderProps) {
  return (
    <div className="bg-[#080808] border border-[#222222] rounded-xl p-4 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-4">
        <div className="h-12 w-12 rounded-full bg-[#10B981]/15 border border-[#10B981]/30 flex items-center justify-center relative">
          <User className="h-6 w-6 text-[#10B981]" />
          <div className="absolute -bottom-1 -right-1 h-4 w-4 bg-emerald-500 border-2 border-slate-900 rounded-full"></div>
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            Officer Workspace
            <span className="bg-[#0D0D0D] text-[#F5F5F5] text-[10px] px-2 py-0.5 rounded font-mono border border-[#2A2A2A]">
              {user?.full_name || 'Loading...'}
            </span>
          </h1>
          <p className="text-xs text-[#9A9A9A] mt-1 flex items-center gap-2">
            <Shield className="h-3 w-3 text-[#666666]" />
            Beat Assignment: Sector 7G
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex flex-col items-end">
          <span className="text-[10px] font-bold text-[#666666] uppercase tracking-widest">Network Status</span>
          <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
            <Radio className="h-3 w-3" /> SECURE UPLINK
          </span>
        </div>
        <div className="h-10 w-px bg-[#0D0D0D]"></div>
        <div className="flex flex-col items-end">
          <span className="text-[10px] font-bold text-[#666666] uppercase tracking-widest">Shift Status</span>
          <span className="text-xs font-mono text-[#10B981] flex items-center gap-1">
            <Activity className="h-3 w-3" /> ON DUTY
          </span>
        </div>
      </div>
    </div>
  );
}
