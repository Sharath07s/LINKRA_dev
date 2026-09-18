"use client";

import DashboardLayout from "@/components/DashboardLayout";
import StateThreatOverview from "@/components/ExecutiveDashboard/StateThreatOverview";
import DistrictRankings from "@/components/ExecutiveDashboard/DistrictRankings";
import EmergingThreats from "@/components/ExecutiveDashboard/EmergingThreats";
import HighRiskOffenders from "@/components/ExecutiveDashboard/HighRiskOffenders";
import HighRiskNetworks from "@/components/ExecutiveDashboard/HighRiskNetworks";
import CrimeHotspotsMap from "@/components/ExecutiveDashboard/CrimeHotspotsMap";
import AIExecutiveBriefing from "@/components/ExecutiveDashboard/AIExecutiveBriefing";

export default function ExecutiveDashboardPage() {
  return (
    <DashboardLayout>
      <div className="flex flex-col h-full space-y-6">
        
        {/* Workspace Title */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[#222222] pb-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">Executive Intelligence Dashboard</h1>
            <p className="text-sm text-[#9A9A9A]">State Command Central • Real-time Threat Aggregation</p>
          </div>
          
          <div className="bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-lg text-red-400 text-xs font-bold uppercase tracking-widest flex items-center gap-2">
            <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse" />
            Live Intel Feed
          </div>
        </div>

        {/* Intelligence Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
          
          {/* Top Row: Threat Overview (5) + AI Briefing (7) */}
          <div className="lg:col-span-5 h-[200px]">
            <StateThreatOverview />
          </div>
          <div className="lg:col-span-7 h-[200px]">
            <AIExecutiveBriefing />
          </div>

          {/* Middle Row: Hotspots (4) + District Rankings (5) + Emerging Threats (3) */}
          <div className="lg:col-span-4 h-[350px]">
            <CrimeHotspotsMap />
          </div>
          <div className="lg:col-span-5 h-[350px]">
            <DistrictRankings />
          </div>
          <div className="lg:col-span-3 h-[350px]">
            <EmergingThreats />
          </div>

          {/* Bottom Row: High Risk Offenders (7) + High Risk Networks (5) */}
          <div className="lg:col-span-7 h-[350px]">
            <HighRiskOffenders />
          </div>
          <div className="lg:col-span-5 h-[350px]">
            <HighRiskNetworks />
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
