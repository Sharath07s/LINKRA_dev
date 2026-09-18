"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import OfficerHeader from "@/components/OfficerWorkspace/OfficerHeader";
import AssignedCasesPanel from "@/components/OfficerWorkspace/AssignedCasesPanel";
import AssignedAlertsPanel from "@/components/OfficerWorkspace/AssignedAlertsPanel";
import NearbyCrimesPanel from "@/components/OfficerWorkspace/NearbyCrimesPanel";
import OfficerCopilot from "@/components/OfficerWorkspace/OfficerCopilot";
import OfficerActionsPanel from "@/components/OfficerWorkspace/OfficerActionsPanel";
import OfficerAuditTimeline from "@/components/OfficerWorkspace/OfficerAuditTimeline";
import OfficerNetworkView from "@/components/OfficerWorkspace/OfficerNetworkView";
import { RealtimeProvider, useRealtime } from "@/components/Providers/RealtimeProvider";
import EventNotificationCenter from "@/components/Predictive/EventNotificationCenter";

function OfficerWorkspaceContent() {
  const { lastEvent } = useRealtime();
  const [cases, setCases] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [actions, setActions] = useState<any[]>([]);
  const [audit, setAudit] = useState<any[]>([]);
  
  // Dummy user object, typically this comes from AuthContext
  const user = { full_name: "John Doe", badge_number: "7489" };

  useEffect(() => {
    fetchCases();
    fetchAlerts();
    fetchActions();
    fetchAudit();
  }, []);

  useEffect(() => {
    if (lastEvent) {
      if (lastEvent.event_type === "ALERT_CREATED" || lastEvent.event_type === "CRIME_CREATED" || lastEvent.event_type === "SUSPECT_UPDATED") {
        fetchCases();
        fetchAlerts();
      }
    }
  }, [lastEvent]);

  const fetchCases = async () => {
    try {
      const res = await apiClient.get("/officer/cases");
      if(res.status === 200) setCases(res.data);
    } catch(e) { console.warn(e) }
  };

  const fetchAlerts = async () => {
    try {
      const res = await apiClient.get("/officer/alerts");
      if(res.status === 200) setAlerts(res.data);
    } catch(e) { console.warn(e) }
  };

  const fetchActions = async () => {
    try {
      const res = await apiClient.get("/officer/actions");
      if(res.status === 200) setActions(res.data);
    } catch(e) { console.warn(e) }
  };

  const fetchAudit = async () => {
    try {
      const res = await apiClient.get("/officer/audit");
      if(res.status === 200) setAudit(res.data);
    } catch(e) { console.warn(e) }
  };

  return (
    <DashboardLayout>
      <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto gap-4 bg-[#050505]">
        
        <OfficerHeader user={user} />
        
        <div className="grid grid-cols-12 gap-4 flex-1 min-h-0">
          
          {/* Left Column: Assignments & Activity */}
          <div className="col-span-3 flex flex-col gap-4 min-h-0">
            <div className="h-1/3 min-h-0">
              <AssignedCasesPanel cases={cases} />
            </div>
            <div className="h-1/3 min-h-0">
              <AssignedAlertsPanel alerts={alerts} />
            </div>
            <div className="h-1/3 min-h-0">
              <NearbyCrimesPanel />
            </div>
          </div>
          
          {/* Middle Column: AI Copilot */}
          <div className="col-span-6 flex flex-col min-h-0">
            <OfficerCopilot />
          </div>
          
          {/* Right Column: Actions, Network, Audit */}
          <div className="col-span-3 flex flex-col gap-4 min-h-0">
            <div className="h-1/3 min-h-0">
              <OfficerActionsPanel actions={actions} fetchActions={fetchActions} />
            </div>
            <div className="h-1/3 min-h-0">
              <OfficerNetworkView />
            </div>
            <div className="h-1/3 min-h-0">
              <OfficerAuditTimeline logs={audit} />
            </div>
          </div>
          
        </div>
      </div>
    </DashboardLayout>
  );
}

export default function OfficerWorkspacePage() {
  return (
    <RealtimeProvider channel="officer-workspace">
      <OfficerWorkspaceContent />
      <EventNotificationCenter />
    </RealtimeProvider>
  );
}
