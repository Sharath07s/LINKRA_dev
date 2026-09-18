"use client";

import React from "react";
import { AlertTriangle, ShieldAlert, AlertCircle, Info, ChevronRight, Activity } from "lucide-react";

interface AlertFeedProps {
  alerts: any[];
  isLoading: boolean;
  onSelectAlert: (alert: any) => void;
  selectedAlertId: string | null;
}

export default function AlertFeed({ alerts, isLoading, onSelectAlert, selectedAlertId }: AlertFeedProps) {
  if (isLoading) {
    return (
      <div suppressHydrationWarning className="flex-1 flex items-center justify-center">
        <Activity className="h-6 w-6 text-[#10B981] animate-spin" />
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center flex-col gap-2 opacity-50">
        <ShieldAlert className="h-8 w-8 text-[#666666]" />
        <span className="text-sm font-bold text-[#9A9A9A]">No active alerts</span>
      </div>
    );
  }

  const getIcon = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case "HIGH": return <ShieldAlert className="h-4 w-4 text-amber-500" />;
      case "MEDIUM": return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default: return <Info className="h-4 w-4 text-[#10B981]" />;
    }
  };

  const getBorderColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return "border-red-500/50";
      case "HIGH": return "border-amber-500/50";
      case "MEDIUM": return "border-yellow-500/50";
      default: return "border-[#10B981]/50";
    }
  };

  return (
    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-700">
      {alerts?.map((alert) => (
        <div 
          key={alert.id}
          onClick={() => onSelectAlert(alert)}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedAlertId === alert.id 
              ? `bg-[#0D0D0D] ${getBorderColor(alert.severity)}` 
              : "bg-[#080808]/50 border-[#222222] hover:bg-[#0D0D0D] hover:border-[#2A2A2A]"
          }`}
        >
          <div className="flex justify-between items-start mb-2">
            <div className="flex items-center gap-2">
              {getIcon(alert.severity)}
              <h4 className="text-sm font-bold text-[#F5F5F5]">{alert.type}</h4>
            </div>
            <span className="text-[10px] text-[#666666] font-mono">
              {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
          
          <h3 className="text-base font-bold text-white mb-2">{alert.title}</h3>
          
          <div className="flex items-center justify-between mt-3">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#9A9A9A] bg-[#050505] px-2 py-0.5 rounded">
              {alert.district}
            </span>
            <div className="flex items-center gap-1 text-xs text-[#10B981] font-medium">
              Details <ChevronRight className="h-3 w-3" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
