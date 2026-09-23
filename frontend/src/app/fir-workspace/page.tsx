"use client";
import { apiClient } from "@/lib/api-client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import FIRHeader from "@/components/FIRWorkspace/FIRHeader";
import AIFIRSummary from "@/components/FIRWorkspace/AIFIRSummary";
import ExtractedEntitiesPanel from "@/components/FIRWorkspace/ExtractedEntitiesPanel";
import RelatedFIRsPanel from "@/components/FIRWorkspace/RelatedFIRsPanel";
import FIRTimeline from "@/components/FIRWorkspace/FIRTimeline";
import FIRMapPanel from "@/components/FIRWorkspace/FIRMapPanel";
import FIRExplainabilityPanel from "@/components/FIRWorkspace/FIRExplainabilityPanel";
import FIRActionsPanel from "@/components/FIRWorkspace/FIRActionsPanel";
import NetworkGraph from "@/components/NetworkGraph";

export default function FIRWorkspacePage() {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
  const [isLoadingGraph, setIsLoadingGraph] = useState(true);

  // In a real scenario, this ID would come from URL query params
  // e.g., const searchParams = useSearchParams(); const firId = searchParams.get('id') || "FIR-101";
  const firId = "BLR-FIR-2026-0399"; 

  useEffect(() => {
    // Reusing the network fetch logic from Sprint 1 for the associated network panel
    const fetchGraphData = async () => {
      try {
        setIsLoadingGraph(true);
        const res = await apiClient.get(`/neo4j/high-risk-networks`);
        const data = res.data;
        
        if (data.nodes && data.edges) {
          const subNodes = data.nodes.slice(0, 6);
          const subNodeIds = subNodes?.map((n: any) => n.id);
          const subEdges = data.edges?.filter((e: any) => subNodeIds.includes(e.source) && subNodeIds.includes(e.target));

          setNodes(subNodes);
          setEdges(subEdges);
        }
      } catch (err) {
        console.warn("Failed to fetch knowledge graph", err);
      } finally {
        setIsLoadingGraph(false);
      }
    };
    
    fetchGraphData();
  }, [firId]);

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
    const neighbors = edges
      ?.filter(e => e.source === node.id || e.target === node.id)
      ?.map(e => e.source === node.id ? e.target : e.source);
    setHighlightedNodeIds([node.id, ...neighbors]);
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-full space-y-6">
        
        {/* Workspace Title */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">FIR Intelligence Workspace</h1>
            <p className="text-sm text-[#9A9A9A]">Deep semantic analysis and entity extraction for individual incident reports.</p>
          </div>
          <div className="h-16 w-full md:w-96">
            <FIRActionsPanel />
          </div>
        </div>

        {/* Top Header */}
        <FIRHeader firId={firId} />

        {/* Intelligence Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column (5/12): AI Summary & Explainability */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            <div className="h-[450px]">
              <AIFIRSummary firId={firId} />
            </div>
            <div className="h-[300px]">
              <FIRExplainabilityPanel firId={firId} />
            </div>
          </div>

          {/* Middle Column (4/12): Entities & Timeline */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="h-[400px]">
              <ExtractedEntitiesPanel firId={firId} />
            </div>
            <div className="h-[350px]">
              <FIRTimeline firId={firId} />
            </div>
          </div>

          {/* Right Column (3/12): Map, Similar FIRs & Network */}
          <div className="lg:col-span-3 flex flex-col gap-6">
            
            <div className="h-[250px]">
              <FIRMapPanel firId={firId} />
            </div>

            <div className="h-[250px]">
              <RelatedFIRsPanel firId={firId} />
            </div>

            <div className="flex-1 min-h-[250px] bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col overflow-hidden">
              <div className="p-3 border-b border-[#222222] flex justify-between items-center bg-[#050505]/50">
                <h3 className="text-sm font-bold text-white tracking-wide">Associated Network</h3>
                {isLoadingGraph && <span className="text-[9px] text-[#10B981] animate-pulse uppercase tracking-widest font-bold">Querying Neo4j...</span>}
              </div>
              <div className="flex-1 p-2 bg-[#050505]/20 relative">
                {!isLoadingGraph && nodes.length > 0 ? (
                  <NetworkGraph 
                    nodes={nodes}
                    edges={edges}
                    selectedNode={selectedNode}
                    highlightedNodeIds={highlightedNodeIds}
                    onNodeClick={handleNodeClick}
                    className="h-full w-full"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-xs text-[#666666] font-semibold">
                    Initializing local graph...
                  </div>
                )}
              </div>
            </div>

          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}
