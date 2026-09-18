"use client";

import React from "react";
import { FolderOpen, User, Car, Smartphone, Network, Map } from "lucide-react";

interface TimelineControlsProps {
  entityType: string;
  setEntityType: (type: string) => void;
  entityId: string;
  setEntityId: (id: string) => void;
}

export default function TimelineControls({ entityType, setEntityType, entityId, setEntityId }: TimelineControlsProps) {
  const tabs = [
    { id: "case", label: "Case Timeline", icon: FolderOpen },
    { id: "suspect", label: "Suspect Timeline", icon: User },
    { id: "vehicle", label: "Vehicle Timeline", icon: Car },
    { id: "phone", label: "Phone Timeline", icon: Smartphone },
    { id: "network", label: "Network Timeline", icon: Network },
    { id: "district", label: "District Timeline", icon: Map },
  ];

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
      <div className="flex flex-wrap gap-2">
        {tabs?.map((tab) => {
          const Icon = tab.icon;
          const isActive = entityType === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setEntityType(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-bold uppercase tracking-wider transition-colors ${
                isActive 
                ? "bg-[#10B981]/15 border-[#10B981]/50 text-[#10B981]" 
                : "bg-[#050505]/50 border-[#222222] text-[#9A9A9A] hover:bg-[#0D0D0D]/50 hover:text-[#F5F5F5]"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="flex items-center gap-2 w-full md:w-auto">
        <input 
          type="text" 
          value={entityId}
          onChange={(e) => setEntityId(e.target.value)}
          placeholder={`Enter ${entityType} ID...`}
          className="bg-[#050505] border border-[#222222] rounded-xl px-4 py-2 text-sm text-[#F5F5F5] focus:outline-none focus:border-[#10B981]/50 w-full md:w-64"
        />
      </div>
    </div>
  );
}
