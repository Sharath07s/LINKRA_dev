"use client";

import { use } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Share2, Download, PlusCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { IntelligenceWorkspace } from "@/components/IntelligenceWorkspace";
import { MapContainer } from "@/components/Investigation/MapContainer";
import { TimelineView } from "@/components/Investigation/TimelineView";
import { EvidenceList } from "@/components/Investigation/EvidenceList";
import { AICopilotPanel } from "@/components/Investigation/AICopilotPanel";
import { ReportView } from "@/components/Investigation/ReportView";
import { CaseSummary } from "@/components/Investigation/CaseSummary";
import { useCrimes } from "@/hooks/useCrimes";
import { LoadingState } from "@/components/ui/loading-state";

export default function InvestigationWorkspace({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const { data: crimes, isLoading } = useCrimes();
  
  const crime = crimes?.find((c: any) => c.id === resolvedParams.id || c.fir_number === resolvedParams.id);

  if (isLoading) {
    return (
      <DashboardLayout>
        <LoadingState message="Loading workspace..." />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        
        {/* Breadcrumb / Back */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Link href="/investigations" className="hover:text-foreground transition-colors flex items-center gap-1">
            <ArrowLeft className="h-4 w-4" />
            Investigations
          </Link>
          <span>/</span>
          <span className="text-foreground font-medium">{crime?.fir_number || resolvedParams.id}</span>
        </div>

        {/* Case Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 p-6 bg-card border border-border shadow-sm rounded-xl">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold tracking-tight text-foreground">
                {crime?.fir_number || resolvedParams.id}
              </h1>
              {crime?.severity && (
                <Badge variant="outline" className={`
                  ${crime.severity === 'High' ? 'border-destructive/30 text-destructive bg-destructive/10' : ''}
                  ${crime.severity === 'Medium' ? 'border-amber-500/30 text-amber-500 bg-amber-500/10' : ''}
                  ${crime.severity === 'Low' ? 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10' : ''}
                `}>
                  {crime.severity.toUpperCase()}
                </Badge>
              )}
              {crime?.status && (
                <Badge variant="outline" className="border-primary/30 text-primary bg-primary/10">
                  {crime.status.toUpperCase()}
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground">
              {crime?.title || "Investigation Workspace"} {crime?.station ? `• ${crime.station}` : ""} {crime?.date ? `• Registered ${crime.date}` : ""}
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="bg-background border-border text-foreground hover:bg-secondary">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button variant="outline" size="sm" className="bg-background border-border text-foreground hover:bg-secondary">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
            <Button size="sm" className="bg-primary hover:bg-primary/90 text-primary-foreground">
              <PlusCircle className="mr-2 h-4 w-4" />
              Add Evidence
            </Button>
          </div>
        </div>

        {/* Workspace Tabs */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="bg-secondary/50 border border-border mb-4 h-12 p-1">
            <TabsTrigger value="overview" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">Overview</TabsTrigger>
            <TabsTrigger value="network" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">Network Graph</TabsTrigger>
            <TabsTrigger value="timeline" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">Timeline</TabsTrigger>
            <TabsTrigger value="map" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">Map</TabsTrigger>
            <TabsTrigger value="evidence" className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm">Evidence</TabsTrigger>
            <TabsTrigger value="report" className="data-[state=active]:bg-emerald-700/80 data-[state=active]:text-white data-[state=active]:shadow-sm">Report</TabsTrigger>
            <TabsTrigger value="copilot" className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white data-[state=active]:shadow-sm">AI Copilot</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-0 outline-none">
            <CaseSummary crime={crime} />
          </TabsContent>

          <TabsContent value="network" className="mt-0 outline-none h-[700px] border border-border rounded-xl bg-card p-4">
            <IntelligenceWorkspace initialFocusId={resolvedParams.id} hideHeader={true} />
          </TabsContent>

          <TabsContent value="timeline" className="mt-0 outline-none">
            <TimelineView />
          </TabsContent>

          <TabsContent value="map" className="mt-0 outline-none">
            <MapContainer />
          </TabsContent>

          <TabsContent value="evidence" className="mt-0 outline-none">
            <EvidenceList />
          </TabsContent>
          
          <TabsContent value="report" className="mt-0 outline-none">
            <ReportView investigationId={resolvedParams.id} />
          </TabsContent>

          <TabsContent value="copilot" className="mt-0 outline-none">
            <AICopilotPanel />
          </TabsContent>
        </Tabs>
        
      </div>
    </DashboardLayout>
  );
}
