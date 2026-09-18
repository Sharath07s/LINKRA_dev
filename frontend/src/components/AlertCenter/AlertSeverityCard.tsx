"use client";

import React from "react";
import { AlertTriangle, ShieldAlert, AlertCircle, Info } from "lucide-react";

interface AlertSeverityCardProps {
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  count: number;
}

export default function AlertSeverityCard({ severity, count }: AlertSeverityCardProps) {
  let config = {
    color: "",
    icon: <Info className="h-5 w-5" />,
    label: "Low Priority"
  };

  switch (severity) {
    case "CRITICAL":
      config = { color: "text-red-500 bg-red-500/10 border-red-500/30", icon: <AlertTriangle className="h-5 w-5 text-red-500" />, label: "Critical Priority" };
      break;
    case "HIGH":
      config = { color: "text-amber-500 bg-amber-500/10 border-amber-500/30", icon: <ShieldAlert className="h-5 w-5 text-amber-500" />, label: "High Priority" };
      break;
    case "MEDIUM":
      config = { color: "text-yellow-500 bg-yellow-500/10 border-yellow-500/30", icon: <AlertCircle className="h-5 w-5 text-yellow-500" />, label: "Medium Priority" };
      break;
    case "LOW":
      config = { color: "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/30", icon: <Info className="h-5 w-5 text-[#10B981]" />, label: "Low Priority" };
      break;
  }

  return (
    <div className={`p-4 rounded-xl border ${config.color} flex items-center justify-between transition-all hover:scale-105 cursor-pointer`}>
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          {config.icon}
          <span className="text-[10px] font-bold uppercase tracking-widest opacity-80">{config.label}</span>
        </div>
        <span className="text-3xl font-bold">{count}</span>
      </div>
    </div>
  );
}
