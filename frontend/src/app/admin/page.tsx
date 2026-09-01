"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import SystemOverview from "@/components/SystemHealth/SystemOverview";
import PostgresHealth from "@/components/SystemHealth/PostgresHealth";
import Neo4jHealth from "@/components/SystemHealth/Neo4jHealth";
import RAGHealth from "@/components/SystemHealth/RAGHealth";
import ProviderHealth from "@/components/SystemHealth/ProviderHealth";
import AlertHealth from "@/components/SystemHealth/AlertHealth";
import APIHealth from "@/components/SystemHealth/APIHealth";
import DataQualityPanel from "@/components/SystemHealth/DataQualityPanel";
import AIHealthSummary from "@/components/SystemHealth/AIHealthSummary";
import InfrastructureHealthPanel from "@/components/SystemHealth/InfrastructureHealthPanel";
import BackupStatusPanel from "@/components/SystemHealth/BackupStatusPanel";
import RecoveryStatusPanel from "@/components/SystemHealth/RecoveryStatusPanel";
import PerformanceMetricsPanel from "@/components/SystemHealth/PerformanceMetricsPanel";
import { RealtimeProvider, useRealtime } from "@/components/Providers/RealtimeProvider";
import EventNotificationCenter from "@/components/Predictive/EventNotificationCenter";

function SystemHealthContent() {
  const { lastEvent } = useRealtime();
  const [data, setData] = useState<any>({
    postgres: null,
    neo4j: null,
    rag: null,
    providers: null,
    alerts: null,
    apis: null,
    dataQuality: null,
    summary: null,
    infrastructureMetrics: null,
    backupStatus: null,
    recoveryStatus: null
  });

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const [postgres, neo4j, rag, providers, alerts, apis, dataQuality, summary, infra, backups, recovery] = await Promise.all([
          apiClient.get("/system-health/postgres").then(r => r.data),
          apiClient.get("/system-health/neo4j").then(r => r.data),
          apiClient.get("/system-health/rag").then(r => r.data),
          apiClient.get("/system-health/providers").then(r => r.data),
          apiClient.get("/system-health/alerts").then(r => r.data),
          apiClient.get("/system-health/apis").then(r => r.data),
          apiClient.get("/system-health/data-quality").then(r => r.data),
          apiClient.get("/system-health/summary").then(r => r.data),
          apiClient.get("/infrastructure/metrics").then(r => r.data).catch(() => null),
          apiClient.get("/infrastructure/backups").then(r => r.data).catch(() => null),
          apiClient.get("/infrastructure/recovery").then(r => r.data).catch(() => null)
        ]);

        setData({ postgres, neo4j, rag, providers, alerts, apis, dataQuality, summary, infrastructureMetrics: infra, backupStatus: backups, recoveryStatus: recovery });
      } catch (err) {
        console.warn("System health check failed", err);
      }
    };

    fetchHealth();
    // Replaced interval with realtime updates
  }, []);

  useEffect(() => {
    if (lastEvent) {
       // Refresh health stats whenever any system event occurs
       const fetchLiveHealth = async () => {
         try {
           const [postgres, neo4j, rag, providers, alerts, apis, dataQuality, summary, realtime, infra, backups, recovery] = await Promise.all([
             apiClient.get("/system-health/postgres").then(r => r.data),
             apiClient.get("/system-health/neo4j").then(r => r.data),
             apiClient.get("/system-health/rag").then(r => r.data),
             apiClient.get("/system-health/providers").then(r => r.data),
             apiClient.get("/system-health/alerts").then(r => r.data),
             apiClient.get("/system-health/apis").then(r => r.data),
             apiClient.get("/system-health/data-quality").then(r => r.data),
             apiClient.get("/system-health/summary").then(r => r.data),
             apiClient.get("/realtime/metrics").then(r => r.data).catch(() => null),
             apiClient.get("/infrastructure/metrics").then(r => r.data).catch(() => null),
             apiClient.get("/infrastructure/backups").then(r => r.data).catch(() => null),
             apiClient.get("/infrastructure/recovery").then(r => r.data).catch(() => null)
           ]);
           setData({ postgres, neo4j, rag, providers, alerts, apis, dataQuality, summary, realtime, infrastructureMetrics: infra, backupStatus: backups, recoveryStatus: recovery });
         } catch(e) {}
       };
       fetchLiveHealth();
    }
  }, [lastEvent]);

  return (
    <DashboardLayout>
      <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto gap-4 bg-slate-950 text-slate-200">
        
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-2xl font-black text-white tracking-widest uppercase">System Health Center</h1>
            <p className="text-xs text-slate-400 font-mono tracking-widest uppercase mt-1">Platform Diagnostics & Observability</p>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-12 grid-rows-3 gap-4 min-h-0">
          
          {/* Row 1: Core Systems */}
          <div className="col-span-3 row-span-1 min-h-0">
            <SystemOverview summary={data.summary} />
          </div>
          <div className="col-span-3 row-span-1 min-h-0">
            <PostgresHealth data={data.postgres} />
          </div>
          <div className="col-span-3 row-span-1 min-h-0">
            <Neo4jHealth data={data.neo4j} />
          </div>
          <div className="col-span-3 row-span-1 min-h-0">
            <RAGHealth data={data.rag} />
          </div>

          {/* Row 2: Logic & API */}
          <div className="col-span-4 row-span-1 min-h-0">
            <AlertHealth data={data.alerts} />
          </div>
          <div className="col-span-4 row-span-1 min-h-0">
            <ProviderHealth providers={data.providers} />
          </div>
          <div className="col-span-4 row-span-1 min-h-0">
            <APIHealth apis={data.apis} />
          </div>

          {/* Row 3: Data Quality & Recommendations */}
          <div className="col-span-6 row-span-1 min-h-0">
            <DataQualityPanel data={data.dataQuality} />
          </div>
          <div className="col-span-6 row-span-1 min-h-0">
            <AIHealthSummary summary={data.summary} />
          </div>

          {/* Row 4: Infrastructure & Production Readiness */}
          <div className="col-span-3 row-span-1 min-h-0">
            <InfrastructureHealthPanel data={data.infrastructureMetrics} />
          </div>
          <div className="col-span-3 row-span-1 min-h-0">
            <BackupStatusPanel data={data.backupStatus} />
          </div>
          <div className="col-span-3 row-span-1 min-h-0">
            <RecoveryStatusPanel data={data.recoveryStatus} />
          </div>
          <div className="col-span-3 row-span-1 min-h-0">
            <PerformanceMetricsPanel data={data.infrastructureMetrics} />
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}

export default function SystemHealthPage() {
  return (
    <RealtimeProvider channel="system-health">
      <SystemHealthContent />
      <EventNotificationCenter />
    </RealtimeProvider>
  );
}
