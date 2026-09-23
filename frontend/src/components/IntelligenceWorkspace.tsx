"use client";
import { apiClient } from "@/lib/api-client";
import { useState, useEffect } from "react";
import { 
  Search, 
  Network, 
  Sliders,
  Bot,
  ChevronDown,
  Users
} from "lucide-react";
import GraphNodeDetails from "@/components/GraphNodeDetails";
import NetworkGraph from "@/components/NetworkGraph";
import EdgeEvidencePanel from "@/components/EdgeEvidencePanel";
import { CopilotPanel } from "@/components/CopilotPanel";
import { CommunityPanel } from "@/components/CommunityPanel";

interface InvestigationOption {
  id: string;
  summary?: string;
  status?: string;
  crime_id?: string;
}

interface IntelligenceWorkspaceProps {
  initialFocusId?: string | null;
  hideHeader?: boolean;
}

export function IntelligenceWorkspace({ initialFocusId, hideHeader = false }: IntelligenceWorkspaceProps) {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [selectedEdge, setSelectedEdge] = useState<any>(null);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [showCommunities, setShowCommunities] = useState(false);
  
  const [investigations, setInvestigations] = useState<InvestigationOption[]>([]);
  const [selectedInvestigationId, setSelectedInvestigationId] = useState<string>("");
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // Fetch investigations
    const fetchInvestigations = async () => {
      try {
        const res = await apiClient.get("/investigations/");
        setInvestigations(res.data || []);
      } catch (err) {
        console.error("Failed to load investigations", err);
      }
    };
    fetchInvestigations();
  }, []);

  useEffect(() => {
    const fetchGraphData = async () => {
      if (!selectedInvestigationId) {
        setNodes([]);
        setEdges([]);
        setIsLoading(false);
        return;
      }
      try {
        setIsLoading(true);
        let endpoint = `/graph/investigations/${encodeURIComponent(selectedInvestigationId)}`; 
        if (initialFocusId) {
            // we could combine them, but for this milestone we stick to the investigation graph
            // or just load the investigation graph and focus the node
        }
        
        const res = await apiClient.get(endpoint);
        const data = res.data;
        
        if (data && data.nodes && data.nodes.length > 0) {
          setNodes(data.nodes);
          setEdges(data.edges || []);
          resetSelection();
          if (initialFocusId) {
             const matchedNode = data.nodes.find((n: any) => n.id === initialFocusId);
             if (matchedNode) {
                 setSelectedNode(matchedNode);
                 // Highlight neighbors
                 const neighbors = (data.edges || [])
                   .filter((e: any) => e.source === matchedNode.id || e.target === matchedNode.id)
                   .map((e: any) => e.source === matchedNode.id ? e.target : e.source);
                 setHighlightedNodeIds([matchedNode.id, ...neighbors]);
             }
          }
        } else {
          setNodes([]);
          setEdges([]);
        }
      } catch (err) {
        console.warn("Failed to fetch case knowledge graph", err);
        setNodes([]);
        setEdges([]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchGraphData();
  }, [selectedInvestigationId, initialFocusId]);

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
    setSelectedEdge(null);
    const neighbors = edges
      ?.filter(e => e.source === node.id || e.target === node.id)
      ?.map(e => e.source === node.id ? e.target : e.source);
    setHighlightedNodeIds([node.id, ...neighbors]);
  };

  const handleEdgeClick = (edge: any) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
    setHighlightedNodeIds([edge.source, edge.target]);
  };

  const resetSelection = () => {
    setSelectedNode(null);
    setSelectedEdge(null);
    setHighlightedNodeIds([]);
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    // Check locally first
    const matchedNode = nodes.find(n => n.label.toLowerCase().includes(searchQuery.toLowerCase()));
    if (matchedNode) {
      handleNodeClick(matchedNode);
      return;
    }

    try {
        setIsLoading(true);
        // Case-specific search filtering is done purely on the frontend for now, or via API if the backend supported it
        // We'll just rely on the API for global search, but wait - the requirements said search must be case-aware.
        // If it's just searching nodes in the CURRENT graph:
        // Already handled above! If the user wants to search for something not in the graph, it's confusing.
        // I will just rely on the local search above, and if not found, we don't switch cases automatically.
        alert("Entity not found in the current investigation graph.");
        resetSelection();
    } catch (err) {
        console.error("Search failed:", err);
    } finally {
        setIsLoading(false);
    }
  };

  if (!isClient) return null;

  const currentInvestigation = investigations.find(inv => inv.id === selectedInvestigationId);

  return (
    <div className="space-y-6 h-full flex flex-col w-full">
      {!hideHeader && (
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">Criminal Relationship Graph</h1>
            <p className="text-sm text-[#9A9A9A]">Discovering multi-degree associations, shared assets, and common modus operandi</p>
          </div>
          
          <div className="flex items-center gap-3">
            <select
              value={selectedInvestigationId}
              onChange={(e) => setSelectedInvestigationId(e.target.value)}
              className="bg-[#050505] border border-[#222222] rounded-xl px-4 py-2 text-sm text-[#F5F5F5] focus:outline-none focus:ring-1 focus:ring-[#10B981] max-w-[300px]"
            >
              <option value="">-- Select an Investigation --</option>
              {investigations.map(inv => (
                <option key={inv.id} value={inv.id}>
                  {inv.summary ? (inv.summary.substring(0, 50) + (inv.summary.length > 50 ? '...' : '')) : `Case ${inv.id.substring(0,8)}`}
                </option>
              ))}
            </select>
            <div className="flex items-center gap-1.5 rounded-full bg-[#10B981]/10 border border-[#10B981]/20 px-3 py-2 text-[10px] font-bold text-[#10B981]">
              <Network className="h-3.5 w-3.5 animate-pulse" />
              <span>NEO4J ONLINE</span>
            </div>
          </div>
        </div>
      )}

      {/* Search Toolbar */}
      <div className="bg-[#080808]/40 border border-[#222222] p-4 rounded-2xl flex flex-col sm:flex-row gap-3 items-center w-full">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-[#666666]">
            <Search className="h-4 w-4" />
          </div>
          <input
            type="text"
            className="w-full bg-[#050505] border border-slate-850 rounded-xl pl-10 pr-4 py-2.5 text-xs text-[#F5F5F5] placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-[#10B981]"
            placeholder="Search suspect profile or node name (e.g. 'Vicky Saluja', 'Kariya Raja')..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
        
        <div className="flex gap-2 w-full sm:w-auto">
          {selectedNode && (
            <button
              onClick={resetSelection}
              className="flex-1 sm:flex-initial px-4 py-2.5 bg-[#050505] hover:bg-[#080808] border border-[#222222] text-xs font-semibold text-[#9A9A9A] rounded-xl transition-colors"
            >
              Clear Focus
            </button>
          )}
          <button className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2.5 bg-[#050505] hover:bg-[#080808] border border-[#222222] text-xs font-semibold text-[#9A9A9A] rounded-xl transition-colors">
            <Sliders className="h-4 w-4" />
            <span>Edge Weight</span>
          </button>
          <button 
            onClick={() => setShowCommunities(prev => !prev)}
            className={`flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2.5 border text-xs font-semibold rounded-xl transition-colors ${showCommunities ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300' : 'bg-[#050505] hover:bg-[#080808] border-[#222222] text-[#9A9A9A]'}`}
          >
            <Users className="h-4 w-4" />
            <span>Communities</span>
          </button>
        </div>
      </div>

      {/* Main interactive panel */}
      <div className="flex-1 min-h-[500px] grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch w-full">
        
        <div className="lg:col-span-8 bg-[#050505]/40 border border-[#222222] rounded-2xl flex flex-col p-2 relative overflow-hidden">
          {!selectedInvestigationId ? (
            <div className="flex-1 flex flex-col items-center justify-center space-y-3 opacity-60 p-6">
              <Network className="h-12 w-12 text-[#666666] mb-2" />
              <h3 className="text-[#F5F5F5] font-semibold text-lg">No Investigation Selected</h3>
              <p className="text-[#666666] text-sm max-w-sm text-center">
                Please select a case from the dropdown above to view its relationship graph.
              </p>
            </div>
          ) : nodes.length > 0 ? (
            <>
              <NetworkGraph 
                nodes={nodes}
                edges={edges}
                selectedNode={selectedNode}
                selectedEdge={selectedEdge}
                highlightedNodeIds={highlightedNodeIds}
                onNodeClick={handleNodeClick}
                onEdgeClick={handleEdgeClick}
                className="w-full flex-1 flex items-center justify-center"
              />
              {selectedEdge && (
                <EdgeEvidencePanel
                  edge={selectedEdge}
                  onClose={() => setSelectedEdge(null)}
                />
              )}
              <div className="absolute top-4 left-4 bg-[#080808]/90 border border-slate-850 p-3 rounded-xl text-[9px] space-y-1.5 z-10 pointer-events-none">
                <span className="font-bold text-slate-350 block uppercase">Node Dictionary</span>
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-1.5 text-[#9A9A9A]">
                    <span className="h-2.5 w-2.5 rounded-full bg-blue-950 border border-blue-400" />
                    <span>Suspect Profile (Neo4j Node)</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#9A9A9A]">
                    <span className="h-2.5 w-2.5 rounded-full bg-red-950 border border-red-500" />
                    <span>Crime Incident (CCTNS Case)</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#9A9A9A]">
                    <span className="h-2.5 w-2.5 rounded-full bg-purple-950 border border-purple-400" />
                    <span>Phone Log (CDR Record)</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[#9A9A9A]">
                    <span className="h-2.5 w-2.5 rounded-full bg-amber-950 border border-amber-400" />
                    <span>Linked Vehicle (ANPR Sighting)</span>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center space-y-3 opacity-60 p-6">
              <Network className="h-12 w-12 text-[#666666] mb-2" />
              <h3 className="text-[#F5F5F5] font-semibold text-lg">No Graph Data Available</h3>
              <p className="text-[#666666] text-sm max-w-sm text-center">
                No relationships or entities available for this investigation.
              </p>
            </div>
          )}
        </div>

        <div className="lg:col-span-4 flex flex-col gap-4">
          <div className="bg-[#080808]/40 border border-[#222222] p-5 rounded-2xl">
            <h4 className="font-bold text-white text-sm uppercase tracking-wider mb-2">
              {currentInvestigation ? "ACTIVE CASE" : "Network Parameters"}
            </h4>
            {currentInvestigation && (
              <p className="text-xs text-[#10B981] mb-4 break-words">
                {currentInvestigation.summary ? currentInvestigation.summary : `CASE ID: ${currentInvestigation.id}`}
              </p>
            )}
            <div className="grid grid-cols-2 gap-2 text-center text-xs">
              <div className="bg-[#050505]/40 p-2.5 rounded-lg border border-slate-850">
                <span className="text-[#666666] block text-[9px] uppercase font-bold">Total Nodes</span>
                <span className="text-sm font-bold text-[#F5F5F5]">{nodes.length} nodes</span>
              </div>
              <div className="bg-[#050505]/40 p-2.5 rounded-lg border border-slate-850">
                <span className="text-[#666666] block text-[9px] uppercase font-bold">Relationships</span>
                <span className="text-sm font-bold text-[#F5F5F5]">{edges.length} links</span>
              </div>
            </div>
          </div>
          <div className="flex-1 bg-[#080808]/40 border border-[#222222] p-5 rounded-2xl flex flex-col min-h-[300px]">
            <GraphNodeDetails 
              selectedNode={selectedNode} 
              edges={edges} 
              nodes={nodes} 
              onNodeClick={handleNodeClick} 
            />
          </div>

          {/* AI Copilot Accordion */}
          <div className="flex flex-col">
            <button
              onClick={() => setCopilotOpen(prev => !prev)}
              className="flex items-center gap-2 w-full px-4 py-2.5 bg-[#10B981]/10 hover:bg-[#10B981]/15 border border-[#10B981]/30 rounded-xl text-xs font-bold text-[#10B981] transition-colors"
            >
              <Bot className="h-3.5 w-3.5" />
              <span>AI Copilot</span>
              {selectedNode && <span className="ml-auto text-[8px] bg-blue-950 border border-blue-700 px-1.5 py-0.5 rounded text-[#10B981]">Node Context Active</span>}
              <ChevronDown className={`h-3.5 w-3.5 ml-auto transition-transform ${copilotOpen ? "rotate-180" : ""}`} />
            </button>
            {copilotOpen && (
              <div className="h-[380px] mt-2">
                <CopilotPanel entityId={selectedNode?.id ?? undefined} />
              </div>
            )}
          </div>
          
          {showCommunities && (
            <CommunityPanel />
          )}
        </div>
      </div>
    </div>
  );
}
