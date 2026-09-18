"use client";

import React from "react";
import DashboardLayout from "@/components/DashboardLayout";
import ForecastOverview from "@/components/Predictive/ForecastOverview";
import FutureHotspots from "@/components/Predictive/FutureHotspots";
import RecidivismIntelligence from "@/components/Predictive/RecidivismIntelligence";
import NetworkGrowth from "@/components/Predictive/NetworkGrowth";
import AIPredictiveBriefing from "@/components/Predictive/AIPredictiveBriefing";
import ValidationMetrics from "@/components/Predictive/ValidationMetrics";
import PredictiveExplainabilityPanel from "@/components/Predictive/PredictiveExplainabilityPanel";
import ModelHealthPanel from "@/components/Predictive/ModelHealthPanel";
import PredictionDriftPanel from "@/components/Predictive/PredictionDriftPanel";
import ReliabilityDashboard from "@/components/Predictive/ReliabilityDashboard";
import { Radar } from "lucide-react";
import { RealtimeProvider } from "@/components/Providers/RealtimeProvider";
import EventNotificationCenter from "@/components/Predictive/EventNotificationCenter";

function PredictiveIntelligenceContent() {
  return (
    <DashboardLayout>
      <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto gap-4 bg-[#050505] text-[#F5F5F5]">
        
        <div className="flex items-center justify-between border-b border-[#222222] pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#10B981]/10 rounded-lg border border-[#10B981]/20">
              <Radar className="h-6 w-6 text-[#10B981]" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-widest uppercase">Predictive Intelligence</h1>
              <p className="text-xs text-[#9A9A9A] font-mono tracking-widest uppercase mt-1">Forecasting & Risk Assessment Engine</p>
            </div>
          </div>
          <div className="text-right">
             <span className="text-[10px] font-mono bg-[#10B981]/10 text-[#10B981] px-2 py-1 rounded border border-[#10B981]/30">
               MODELS: ONLINE
             </span>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-12 grid-rows-3 gap-4 min-h-0">
          
          {/* Row 1: Core Forecasts */}
          <div className="col-span-3 row-span-1 min-h-0">
            <ForecastOverview />
          </div>
          <div className="col-span-4 row-span-1 min-h-0">
            <FutureHotspots />
          </div>
          <div className="col-span-5 row-span-1 min-h-0">
            <NetworkGrowth />
          </div>

          {/* Row 2: AI Briefing & Recidivism */}
          <div className="col-span-8 row-span-2 min-h-0">
            <AIPredictiveBriefing />
          </div>
          <div className="col-span-4 row-span-2 min-h-0 flex flex-col gap-4">
             <div className="flex-1 min-h-0">
               <RecidivismIntelligence />
             </div>
             <div className="flex-1 min-h-0">
               <PredictiveExplainabilityPanel />
             </div>
             <div className="flex-1 min-h-0 flex gap-3">
               <div className="flex-1">
                 <ModelHealthPanel />
               </div>
               <div className="flex-1">
                 <PredictionDriftPanel />
               </div>
               <div className="flex-1">
                 <ReliabilityDashboard />
               </div>
             </div>
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}

export default function PredictiveIntelligencePage() {
  return (
    <RealtimeProvider channel="predictive">
      <PredictiveIntelligenceContent />
      <EventNotificationCenter />
    </RealtimeProvider>
  );
}
