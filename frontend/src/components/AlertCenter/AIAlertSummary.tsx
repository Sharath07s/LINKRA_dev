"use client";

import React from "react";
import { BrainCircuit, AlertTriangle } from "lucide-react";

interface AIAlertSummaryProps {
  alerts: any[];
}

export default function AIAlertSummary({ alerts }: AIAlertSummaryProps) {
  const criticalCount = alerts?.filter(a => a.severity === 'CRITICAL').length;
  
  // This is a synthetic summary generated client-side for rapid rendering. 
  // In a full implementation, this could call POST /api/v1/alerts/briefing
  const summaryText = alerts.length === 0 
    ? "System state nominal. No actionable intelligence alerts present."
    : `Command Center detects ${alerts.length} active alerts. ${criticalCount > 0 ? `Urgent attention required: ${criticalCount} CRITICAL threats actively expanding.` : 'Monitoring emerging medium-to-high risk anomalies.'}`;

  return (
    <div className="bg-[#080808]/60 border border-[#10B981]/20 rounded-xl p-4 flex gap-4 items-start shadow-inner shadow-blue-900/10 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
        <BrainCircuit className="h-24 w-24" />
      </div>
      
      <div className="p-2 bg-[#10B981]/15 rounded-lg border border-[#10B981]/30 flex-shrink-0">
        <BrainCircuit className="h-6 w-6 text-[#10B981]" />
      </div>
      
      <div className="flex-1 z-10">
        <h3 className="text-xs font-bold text-[#10B981] uppercase tracking-widest mb-1">AI Intelligence Brief</h3>
        <p className="text-sm text-[#F5F5F5] leading-relaxed font-serif">
          {summaryText}
        </p>
      </div>
    </div>
  );
}
