"use client";

import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import TimelineControls from "@/components/TimelineIntelligence/TimelineControls";
import TimelineExplorer from "@/components/TimelineIntelligence/TimelineExplorer";
import AITimelineAnalysisPanel from "@/components/TimelineIntelligence/AITimelineAnalysisPanel";
import { Download } from "lucide-react";

export default function TimelineIntelligencePage() {
  const [entityType, setEntityType] = useState("case");
  const [entityId, setEntityId] = useState("");

  return (
    <DashboardLayout>
      <div className="flex flex-col h-full space-y-6">
        
        {/* Workspace Title */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">Timeline Intelligence Platform</h1>
            <p className="text-sm text-slate-400">Chronological reconstruction of criminal activities across all dimensions.</p>
          </div>
          
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600/20 border border-blue-500/50 text-blue-400 hover:bg-blue-600/30 transition-colors text-xs font-bold uppercase tracking-wider">
            <Download className="h-4 w-4" />
            Export Timeline Report
          </button>
        </div>

        {/* Global Controls */}
        <TimelineControls 
          entityType={entityType}
          setEntityType={setEntityType}
          entityId={entityId}
          setEntityId={setEntityId}
        />

        {/* Intelligence Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-[600px]">
          
          {/* Left Column (8/12): Main Interactive Explorer */}
          <div className="lg:col-span-8 flex flex-col h-full">
            <TimelineExplorer 
              entityType={entityType}
              entityId={entityId}
            />
          </div>

          {/* Right Column (4/12): AI Context & Analysis */}
          <div className="lg:col-span-4 flex flex-col h-full">
            <AITimelineAnalysisPanel 
              entityType={entityType}
              entityId={entityId}
            />
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
