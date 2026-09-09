"use client";
import { apiClient } from "@/lib/api-client";
import { useState, useEffect } from "react";
import { investigationService, Investigation } from "@/services/investigation.service";
import DashboardLayout from "@/components/DashboardLayout";
import { CaseSummary } from "@/components/Investigation/CaseSummary";
import AICopilot from "@/components/Investigation/AICopilot";
import EvidenceIntel from "@/components/Investigation/EvidenceIntel";
import NetworkGraph from "@/components/NetworkGraph";
import CaseTimeline from "@/components/Investigation/CaseTimeline";
import CaseMapPanel from "@/components/Investigation/CaseMapPanel";
import InvestigationActionsPanel from "@/components/Investigation/InvestigationActionsPanel";
import ThreatAssessmentPanel from "@/components/Investigation/ThreatAssessmentPanel";
import InvestigationAuditTrail from "@/components/Investigation/InvestigationAuditTrail";
import InvestigationHealthPanel from "@/components/Investigation/InvestigationHealthPanel";

export default function InvestigationBoardPage() {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedInvestigation, setSelectedInvestigation] = useState<Investigation | null>(null);

  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [nodeCoordinates, setNodeCoordinates] = useState<Record<string, {x: number, y: number}>>({});
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentCase, setCurrentCase] = useState<any>(null);

  useEffect(() => {
    const fetchInvestigations = async () => {
      try {
        // Read URL params for specific ID, else pick first
        const params = new URLSearchParams(window.location.search);
        const urlId = params.get('id');
        let activeId = urlId;
        
        if (!activeId) {
          const data = await investigationService.listInvestigations();
          if (data.length > 0) {
            activeId = data[0].id;
          }
        }
        
        if (activeId) {
          const fullCase = await investigationService.getInvestigation(activeId);
          setSelectedInvestigation(fullCase as any);
          setCurrentCase({
            ...fullCase,
            riskLevel: "ANALYZING",
            dateUpdated: new Date().toISOString()
          });
        }
      } catch (err) {
        console.error("Failed to fetch investigations", err);
      }
    };
    fetchInvestigations();
  }, []);

  useEffect(() => {
    if (!selectedInvestigation) return;
    
    const fetchGraphData = async () => {
      try {
        setIsLoading(true);
        // First get entities for this investigation
        const entitiesRes = await apiClient.get(`/investigations/${selectedInvestigation.id}/entities`);
        const entities = entitiesRes.data;
        
        if (entities && entities.length > 0) {
          // Fetch subgraph for the first entity to anchor the graph
          const firstEntityId = entities[0].entity_id;
          const res = await apiClient.get(`/graph/subgraph/${firstEntityId}?depth=2&max_nodes=50`);
          const data = res.data;
          
          if (data.nodes && data.edges) {
            const subNodes = data.nodes;
            const subNodeIds = subNodes?.map((n: any) => n.id);
            const subEdges = data.edges?.filter((e: any) => subNodeIds.includes(e.source) && subNodeIds.includes(e.target));

            setNodes(subNodes);
            setEdges(subEdges);
            
            const coords: Record<string, {x: number, y: number}> = {};
            const cx = 250;
            const cy = 175;
            const r = 100;
            subNodes?.forEach((node: any, idx: number) => {
              const angle = (idx / subNodes.length) * 2 * Math.PI;
              coords[node.id] = {
                x: cx + r * Math.cos(angle),
                y: cy + r * Math.sin(angle)
              };
            });
            setNodeCoordinates(coords);
          }
        } else {
            setNodes([]);
            setEdges([]);
        }
      } catch (err) {
        console.warn("Failed to fetch knowledge graph for investigation", err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchGraphData();
  }, [selectedInvestigation]);

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
    const neighbors = edges
      ?.filter(e => e.source === node.id || e.target === node.id)
      ?.map(e => e.source === node.id ? e.target : e.source);
    setHighlightedNodeIds([node.id, ...neighbors]);
  };

  if (!currentCase) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-[70vh] text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700 animate-pulse">
            <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-white">Loading Investigation...</h2>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col h-full space-y-6">
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">Investigation Workspace</h1>
            <p className="text-sm text-slate-400">Comprehensive case context, AI analysis, and intelligence mapping.</p>
          </div>
          <div className="flex gap-3 h-24">
            <InvestigationActionsPanel investigationId={currentCase.id} />
          </div>
        </div>

        <CaseSummary crime={currentCase as any} />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: AI Copilot & Threat */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="h-[450px]">
              <AICopilot />
            </div>
            <div className="h-[350px]">
              <ThreatAssessmentPanel investigationId={currentCase.id} />
            </div>
            <div className="flex-1">
              <InvestigationHealthPanel investigationId={currentCase.id} />
            </div>
          </div>

          {/* Center Column: Timeline & Evidence */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="h-[500px]">
              <CaseTimeline investigationId={currentCase.id} />
            </div>
            <div className="h-[300px]">
              <EvidenceIntel investigationId={currentCase.id} />
            </div>
          </div>

          {/* Right Column: Geographic & Network Intelligence */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="h-[400px]">
              <CaseMapPanel investigationId={currentCase.id} />
            </div>
            
            <div className="h-[400px] bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col overflow-hidden">
              <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/50">
                <h3 className="text-sm font-bold text-white tracking-wide">Network Intelligence</h3>
                {isLoading && <span className="text-[10px] text-blue-400 animate-pulse uppercase tracking-widest font-bold">Syncing...</span>}
              </div>
              <div className="flex-1 p-2 bg-slate-950/20 relative">
                {!isLoading && nodes.length > 0 ? (
                  <NetworkGraph 
                    nodes={nodes}
                    edges={edges}
                    nodeCoordinates={nodeCoordinates}
                    selectedNode={selectedNode}
                    highlightedNodeIds={highlightedNodeIds}
                    onNodeClick={handleNodeClick}
                    className="h-full w-full"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-xs text-slate-500 font-semibold">
                    Initializing local graph...
                  </div>
                )}
              </div>
            </div>

            <div className="flex-1 min-h-[250px]">
              <InvestigationAuditTrail investigationId={currentCase.id} />
            </div>
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
