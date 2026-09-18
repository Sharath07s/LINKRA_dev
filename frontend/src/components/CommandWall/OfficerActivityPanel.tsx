"use client";

import React from "react";
import { UserCheck } from "lucide-react";

export default function OfficerActivityPanel({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl"></div>;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <UserCheck className="h-4 w-4 text-[#10B981]" /> Active Personnel
        </h3>
      </div>
      <div className="flex-1 flex flex-col justify-center px-4 gap-4">
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-[#9A9A9A]">Officers On Duty</span>
          <span className="text-xl font-mono text-emerald-400">{data.active_officers}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-[#9A9A9A]">Actions Logged Today</span>
          <span className="text-xl font-mono text-[#10B981]">{data.actions_today}</span>
        </div>
      </div>
    </div>
  );
}
