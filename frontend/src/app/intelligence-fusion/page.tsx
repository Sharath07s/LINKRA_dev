"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import FusionOverview from "@/components/IntelligenceFusion/FusionOverview";
import CorrelationExplorer from "@/components/IntelligenceFusion/CorrelationExplorer";
import PriorityMatrix from "@/components/IntelligenceFusion/PriorityMatrix";
import DecisionSupportPanel from "@/components/IntelligenceFusion/DecisionSupportPanel";
import FusionBriefingPanel from "@/components/IntelligenceFusion/FusionBriefingPanel";
import { RealtimeProvider, useRealtime } from "@/components/Providers/RealtimeProvider";
import EventNotificationCenter from "@/components/Predictive/EventNotificationCenter";

function IntelligenceFusionContent() {
  const { lastEvent } = useRealtime();
  const [data, setData] = useState<any>({
    signals: null,
    correlations: null,
    priorities: null,
    recommendations: null
  });

  const fetchFusionData = async () => {
    try {
      const [signals, correlations, priorities, recommendations] = await Promise.all([
        apiClient.get("/fusion/signals").then(r => r.data),
        apiClient.get("/fusion/correlations").then(r => r.data),
        apiClient.get("/fusion/priorities").then(r => r.data),
        apiClient.get("/fusion/recommendations").then(r => r.data)
      ]);

      setData({ signals, correlations, priorities, recommendations });
    } catch (err) {
      console.warn("Intelligence Fusion fetch failed", err);
    }
  };

  useEffect(() => {
    fetchFusionData();
  }, []);

  useEffect(() => {
    if (lastEvent) {
       // Refresh data when realtime stream indicates an update
       fetchFusionData();
    }
  }, [lastEvent]);

  return (
    <DashboardLayout>
      <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto gap-4 bg-[#050505] text-[#F5F5F5]">
        
        <div className="flex items-center justify-between border-b border-[#222222] pb-4">
          <div>
            <h1 className="text-2xl font-black text-white tracking-widest uppercase">Intelligence Fusion</h1>
            <p className="text-xs text-[#9A9A9A] font-mono tracking-widest uppercase mt-1">Cross-System Threat Aggregation & Decision Support</p>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-12 grid-rows-2 gap-4 min-h-0">
          
          {/* Row 1 */}
          <div className="col-span-5 row-span-1 min-h-0">
            <FusionOverview data={data.signals} />
          </div>
          <div className="col-span-4 row-span-1 min-h-0">
            <DecisionSupportPanel data={data.recommendations} />
          </div>
          <div className="col-span-3 row-span-1 min-h-0">
            <PriorityMatrix data={data.priorities} />
          </div>

          {/* Row 2 */}
          <div className="col-span-6 row-span-1 min-h-0">
            <CorrelationExplorer data={data.correlations} />
          </div>
          <div className="col-span-6 row-span-1 min-h-0">
            <FusionBriefingPanel data={data.signals} />
          </div>

        </div>
      </div>
    </DashboardLayout>
  );
}

export default function IntelligenceFusionPage() {
  return (
    <RealtimeProvider channel="intelligence-fusion">
      <IntelligenceFusionContent />
      <EventNotificationCenter />
    </RealtimeProvider>
  );
}
