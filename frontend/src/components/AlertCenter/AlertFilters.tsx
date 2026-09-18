"use client";

import React from "react";
import { Filter } from "lucide-react";

interface AlertFiltersProps {
  activeFilter: string;
  setActiveFilter: (filter: string) => void;
}

export default function AlertFilters({ activeFilter, setActiveFilter }: AlertFiltersProps) {
  const filters = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"];

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
      <div className="bg-[#0D0D0D] p-1.5 rounded-lg mr-2">
        <Filter className="h-4 w-4 text-[#9A9A9A]" />
      </div>
      
      {filters?.map(filter => (
        <button
          key={filter}
          onClick={() => setActiveFilter(filter)}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors ${
            activeFilter === filter 
              ? "bg-[#10B981] text-white" 
              : "bg-[#080808]/50 text-[#9A9A9A] border border-[#2A2A2A] hover:bg-[#0D0D0D]"
          }`}
        >
          {filter}
        </button>
      ))}
    </div>
  );
}
