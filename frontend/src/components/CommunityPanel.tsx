import React, { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { AlertTriangle, Users, Network, Info, CheckCircle2 } from "lucide-react";

export function CommunityPanel() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [algorithm, setAlgorithm] = useState<"louvain" | "leiden">("louvain");

  useEffect(() => {
    const fetchCommunities = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await apiClient.get(`/graph/analytics/communities?algorithm=${algorithm}`);
        setData(res.data);
      } catch (err: any) {
        console.error(`Failed to fetch ${algorithm} communities`, err);
        setError(err.response?.data?.detail || "Failed to fetch community data. Infrastructure may be unreachable.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchCommunities();
  }, [algorithm]);

  return (
    <div className="flex flex-col h-full bg-[#080808]/60 border border-[#222222] rounded-2xl overflow-hidden mt-4">
      <div className="p-4 border-b border-[#222222] bg-[#050505]/40 flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Users className="h-5 w-5 text-indigo-400" />
            <h2 className="font-bold text-white tracking-tight">Graph Communities</h2>
          </div>
          <p className="text-xs text-[#9A9A9A]">
            Groups of entities identified purely from structural graph connectivity.
          </p>
        </div>
        
        {/* Algorithm Selector */}
        <div className="flex bg-[#050505] rounded-xl border border-[#222222] p-1">
          <button
            onClick={() => setAlgorithm("louvain")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              algorithm === "louvain" ? "bg-indigo-600 text-white" : "text-[#9A9A9A] hover:text-[#F5F5F5]"
            }`}
          >
            Louvain
          </button>
          <button
            onClick={() => setAlgorithm("leiden")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              algorithm === "leiden" ? "bg-indigo-600 text-white" : "text-[#9A9A9A] hover:text-[#F5F5F5]"
            }`}
          >
            Leiden
          </button>
        </div>
      </div>

      <div className="p-5 flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full text-[#9A9A9A] text-sm py-10">
            <div className="animate-pulse flex flex-col items-center gap-3">
              <Network className="h-8 w-8 text-indigo-500" />
              <span>Executing {algorithm.charAt(0).toUpperCase() + algorithm.slice(1)} Algorithm...</span>
            </div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-10">
            <div className="p-4 bg-red-950/20 border border-red-900/50 rounded-xl max-w-sm">
              <div className="flex items-center gap-2 text-red-400 mb-2">
                <AlertTriangle className="h-5 w-5" />
                <h3 className="font-bold text-sm">Graph Infrastructure Error</h3>
              </div>
              <p className="text-xs text-red-300/80 mb-3">{error}</p>
              <div className="bg-red-950/40 p-2 rounded-lg text-[10px] text-red-400/70">
                Ensure Neo4j AuraDB is active and accessible. We do not mock this data.
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
             <div className="flex justify-between items-center mb-4">
               <span className="text-sm font-semibold text-[#F5F5F5]">
                 Total Communities: <span className="text-indigo-400">{data?.communities?.length || 0}</span>
               </span>
               <span className="text-[10px] font-mono text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                 <CheckCircle2 className="h-3 w-3 inline mr-1" />
                 REAL GRAPH DATA
               </span>
             </div>
             
             {data?.communities?.length > 0 ? (
               <div className="grid gap-4">
                 {data.communities.map((comm: any) => (
                   <div key={comm.community_id} className="bg-[#0A0A0A] border border-[#222222] rounded-xl p-4">
                     <div className="flex justify-between items-start mb-3">
                       <h4 className="font-bold text-[#F5F5F5]">Community {comm.community_id}</h4>
                       <span className="text-xs font-semibold bg-[#222222] text-[#F5F5F5] px-2 py-1 rounded-lg">
                         Size: {comm.size}
                       </span>
                     </div>
                     
                     <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-[#111111] p-3 rounded-lg border border-[#2A2A2A]">
                          <p className="text-[10px] text-[#666666] uppercase tracking-wider font-bold mb-1">Structurally Influential</p>
                          <p className="text-xs text-indigo-400 font-mono truncate" title={comm.influential_entity || "N/A"}>
                            {comm.influential_entity || "None"}
                          </p>
                        </div>
                        <div className="bg-[#111111] p-3 rounded-lg border border-[#2A2A2A]">
                          <p className="text-[10px] text-[#666666] uppercase tracking-wider font-bold mb-1">Bridge Candidates</p>
                          <p className="text-xs text-[#F5F5F5] font-mono truncate" title={comm.bridge_candidates?.join(", ") || "N/A"}>
                            {comm.bridge_candidates?.length > 0 ? comm.bridge_candidates.length + " candidate(s)" : "None"}
                          </p>
                        </div>
                     </div>
                     
                     <div className="mb-3">
                       <p className="text-[10px] text-[#666666] uppercase tracking-wider font-bold mb-2">Members ({comm.members?.length || 0})</p>
                       <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto pr-1 custom-scrollbar">
                         {comm.members?.slice(0, 50).map((m: any, i: number) => (
                           <span key={i} className="text-[10px] bg-[#1A1A1A] text-[#9A9A9A] px-2 py-1 rounded-md border border-[#333333] truncate max-w-[120px]" title={m.name}>
                             {m.name || m.entity_id}
                           </span>
                         ))}
                         {(comm.members?.length || 0) > 50 && (
                           <span className="text-[10px] bg-[#1A1A1A] text-[#9A9A9A] px-2 py-1 rounded-md border border-[#333333]">
                             +{comm.members.length - 50} more
                           </span>
                         )}
                       </div>
                     </div>
                     
                     {comm.evidence && (
                       <div className="mt-3 pt-3 border-t border-[#222222] flex items-start gap-2">
                         <Info className="h-3.5 w-3.5 text-[#666666] mt-0.5" />
                         <p className="text-[10px] text-[#666666] leading-relaxed">
                           <span className="font-semibold">Provenance:</span> {comm.evidence}
                         </p>
                       </div>
                     )}
                   </div>
                 ))}
               </div>
             ) : (
               <div className="text-center bg-[#050505] border border-[#222222] rounded-xl py-8">
                 <p className="text-[#666666] text-sm">No communities detected</p>
                 <p className="text-[10px] text-[#666666] mt-2 max-w-xs mx-auto">The graph may be too sparse or lack sufficient connectivity to form distinct structural communities.</p>
               </div>
             )}
          </div>
        )}
      </div>
    </div>
  );
}
