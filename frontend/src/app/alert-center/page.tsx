"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { ShieldAlert } from "lucide-react";
import AlertSeverityCard from "@/components/AlertCenter/AlertSeverityCard";
import AlertFilters from "@/components/AlertCenter/AlertFilters";
import AlertFeed from "@/components/AlertCenter/AlertFeed";
import AlertDetailsPanel from "@/components/AlertCenter/AlertDetailsPanel";
import AIAlertSummary from "@/components/AlertCenter/AIAlertSummary";
import AlertMapOverlay from "@/components/AlertCenter/AlertMapOverlay";
import { RealtimeProvider, useRealtime } from "@/components/Providers/RealtimeProvider";
import EventNotificationCenter from "@/components/Predictive/EventNotificationCenter";

function AlertCenterContent() {
  const { lastEvent } = useRealtime();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);

  useEffect(() => {
    fetchAlerts();
    // Polling replaced with realtime updates
  }, []);

  useEffect(() => {
    if (lastEvent) {
      if (lastEvent.event_type === "ALERT_CREATED" || lastEvent.event_type === "ALERT_RESOLVED" || lastEvent.event_type === "CRIME_CREATED") {
        fetchAlerts();
      }
    }
  }, [lastEvent]);

  const fetchAlerts = async () => {
    try {
      // The base /api/v1/alerts endpoint triggers the AlertEngine to evaluate current intelligence
      const res = await apiClient.get("/alerts/open");
      if (res.status === 200) {
        const data = res.data;
        setAlerts(data);
      }
    } catch (err) {
      console.warn("Failed to fetch alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (id: string) => {
    try {
      const res = await apiClient.post(`/alerts/${id}/resolve`);
      if (res.status === 200) {
        setAlerts(alerts?.filter(a => a.id !== id));
        if (selectedAlert?.id === id) {
          setSelectedAlert(null);
        }
      }
    } catch (err) {
      console.warn("Failed to resolve alert", err);
    }
  };

  const filteredAlerts = alerts?.filter(a => {
    if (activeFilter === "ALL") return true;
    return a.severity === activeFilter;
  });

  const criticalCount = alerts?.filter(a => a.severity === "CRITICAL").length;
  const highCount = alerts?.filter(a => a.severity === "HIGH").length;
  const mediumCount = alerts?.filter(a => a.severity === "MEDIUM").length;
  const lowCount = alerts?.filter(a => a.severity === "LOW").length;

  return (
    <DashboardLayout>
      <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto gap-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/10 rounded-lg border border-red-500/20">
              <ShieldAlert className="h-6 w-6 text-red-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Alert Center</h1>
              <p className="text-sm text-slate-400 font-mono">Live Intelligence Threat Stream</p>
            </div>
          </div>
        </div>

        {/* Top KPIs */}
        <div className="grid grid-cols-4 gap-4">
          <AlertSeverityCard severity="CRITICAL" count={criticalCount} />
          <AlertSeverityCard severity="HIGH" count={highCount} />
          <AlertSeverityCard severity="MEDIUM" count={mediumCount} />
          <AlertSeverityCard severity="LOW" count={lowCount} />
        </div>

        {/* AI Briefing */}
        <AIAlertSummary alerts={alerts} />

        {/* Main Content Area */}
        <div className="flex-1 grid grid-cols-12 gap-6 min-h-0">
          
          {/* Left Column: Feed */}
          <div className="col-span-5 flex flex-col gap-4 bg-slate-950/50 p-4 rounded-2xl border border-slate-800">
            <AlertFilters activeFilter={activeFilter} setActiveFilter={setActiveFilter} />
            <AlertFeed 
              alerts={filteredAlerts} 
              isLoading={loading} 
              onSelectAlert={setSelectedAlert}
              selectedAlertId={selectedAlert?.id || null}
            />
          </div>
          
          {/* Right Column: Details & Map */}
          <div className="col-span-7 flex flex-col gap-6 min-h-0">
            <div className="flex-1">
              <AlertDetailsPanel alert={selectedAlert} onResolve={handleResolve} />
            </div>
            <div className="h-[250px]">
              <AlertMapOverlay alerts={alerts} />
            </div>
          </div>

        </div>
      </div>
    </DashboardLayout>
  );
}

export default function AlertCenterPage() {
  return (
    <RealtimeProvider channel="alerts">
      <AlertCenterContent />
      <EventNotificationCenter />
    </RealtimeProvider>
  );
}
