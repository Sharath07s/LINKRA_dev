import { Network, Info, Activity, AlertTriangle, Link2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Badge } from "@/components/ui/badge";

export default function GraphNodeDetails({ selectedNode, edges, nodes, onNodeClick }: any) {
  const router = useRouter();
  const [explainabilityData, setExplainabilityData] = useState<any>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);

  useEffect(() => {
    if (selectedNode) {
      setLoadingAnalytics(true);
      apiClient.get(`/explainability/entity/${selectedNode.id}`)
        .then((res) => {
          setExplainabilityData(res.data);
        })
        .catch((err) => {
          console.error("Failed to load explainability data:", err);
          setExplainabilityData(null);
        })
        .finally(() => {
          setLoadingAnalytics(false);
        });
    }
  }, [selectedNode]);

  const degree = explainabilityData?.structural_analytics?.degree || { total_degree: 0, in_degree: 0, out_degree: 0 };
  const distribution = explainabilityData?.structural_analytics?.distribution || [];
  const anomalies = explainabilityData?.anomalies || [];
  const potentialLinks = explainabilityData?.potential_links || [];
  const evidence = explainabilityData?.evidence || [];
  const observedRelationships = explainabilityData?.observed_relationships || [];

  if (!selectedNode) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 space-y-2">
        <Network className="h-8 w-8 text-slate-600" />
        <p className="text-xs font-semibold">Focus a Node Link</p>
        <p className="text-[10px] text-slate-500 max-w-[180px]">Select any icon node in the network constellation to view full relationship intelligence</p>
      </div>
    );
  }

  const directEdges = edges?.filter((e: any) => e.source === selectedNode.id || e.target === selectedNode.id);

  return (
    <AnimatePresence mode="wait">
      <motion.div 
        key={selectedNode.id}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
        className="space-y-4 flex-1 flex flex-col"
      >
        <div className="border-b border-slate-800 pb-3">
          <div className="flex justify-between items-center">
            <span className="text-[9px] font-bold text-blue-400 uppercase tracking-widest block font-mono">
              Clearance Level: Active
            </span>
            <span className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase ${
              selectedNode.risk === "High" ? "bg-red-500/10 text-red-400" : "bg-amber-500/10 text-amber-400"
            }`}>
              {selectedNode.risk} Threat
            </span>
          </div>
          <h3 className="font-bold text-white text-base mt-1 leading-snug">{selectedNode.label}</h3>
        </div>

        <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-850 text-center">
          <span className="text-[9px] text-slate-500 block uppercase font-bold">Risk Assessment index</span>
          <span className="text-lg font-extrabold text-red-400">{selectedNode.rating} / 10</span>
        </div>

        <div className="space-y-1 text-xs">
          <span className="text-[9px] font-bold text-slate-500 uppercase block">Profile Summary</span>
          <p className="text-slate-300 leading-normal bg-slate-950/40 p-3 rounded-lg border border-slate-850">
            {selectedNode.desc}
          </p>
        </div>

        {/* M1.8 Degree Analytics */}
        <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
          <span className="text-[9px] text-slate-400 block uppercase font-bold mb-2 flex items-center gap-1">
            <Activity className="h-3 w-3" /> Connectivity Metrics (M1.8)
          </span>
          {loadingAnalytics ? (
             <div className="text-[10px] text-slate-500 animate-pulse">Calculating network metrics...</div>
          ) : (
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                <span className="text-[8px] text-slate-500 uppercase block">Total</span>
                <span className="text-xs font-bold text-white">{degree?.total_degree || 0}</span>
              </div>
              <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                <span className="text-[8px] text-slate-500 uppercase block">In</span>
                <span className="text-xs font-bold text-blue-400">{degree?.in_degree || 0}</span>
              </div>
              <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                <span className="text-[8px] text-slate-500 uppercase block">Out</span>
                <span className="text-xs font-bold text-emerald-400">{degree?.out_degree || 0}</span>
              </div>
            </div>
          )}
        </div>

        {/* M1.8 Relationship Distribution */}
        {!loadingAnalytics && distribution.length > 0 && (
          <div className="space-y-1">
            <span className="text-[9px] font-bold text-slate-500 uppercase block">Relationship Types</span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {distribution.map((dist: any, idx: number) => (
                <span key={idx} className="px-1.5 py-0.5 rounded text-[8px] font-mono border border-slate-700 bg-slate-800 text-slate-300">
                  {dist.rel_type}: <span className="text-white font-bold">{dist.count}</span>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* M1.9 Anomaly Signals */}
        <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800 relative overflow-hidden">
          <span className="text-[9px] text-slate-400 block uppercase font-bold mb-2 flex items-center gap-1">
            <AlertTriangle className="h-3 w-3 text-red-500" /> Anomaly Signals (M1.9)
          </span>
          {loadingAnalytics ? (
            <div className="text-[10px] text-slate-500 animate-pulse">Analyzing structure...</div>
          ) : anomalies.length > 0 ? (
            <div className="space-y-2 relative z-10">
              {anomalies.map((anom: any, idx: number) => (
                <div key={idx} className="bg-slate-950 border-l-2 border-red-500 p-2 rounded relative">
                  <div className="flex justify-between items-start">
                    <span className="text-[9px] font-bold text-red-400 uppercase">{anom.anomaly_type.replace(/_/g, ' ')}</span>
                    <span className="text-[8px] px-1 py-0.5 bg-red-950 text-red-300 rounded border border-red-900/50">Score: {anom.score.toFixed(2)}</span>
                  </div>
                  <p className="text-[9px] text-slate-400 mt-1 leading-tight">{anom.reason}</p>
                  
                  {anom.explanation && (
                    <div className="mt-2 bg-slate-900/50 border border-slate-800 p-2 rounded">
                      <span className="text-[8px] uppercase font-bold text-slate-500 mb-1 block">Explanation</span>
                      <p className="text-[9px] text-slate-300 italic">{anom.explanation.reason}</p>
                    </div>
                  )}

                  <div className="flex justify-between text-[8px] text-slate-500 mt-1.5 border-t border-slate-800 pt-1">
                    <span>Observed: <span className="text-slate-300 font-mono">{anom.observed_value}</span></span>
                    <span>Baseline: <span className="text-slate-300 font-mono">{anom.baseline_value}</span></span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-[10px] text-slate-500 italic py-1 text-center bg-slate-950/40 rounded border border-slate-800/50">
              No structural anomalies detected.
            </div>
          )}
        </div>

        <div className="space-y-2 flex-1">
          <span className="text-[9px] font-bold text-slate-400 uppercase block tracking-wider">Direct Links ({directEdges.length})</span>
          <div className="space-y-1.5 max-h-[160px] overflow-y-auto pr-1">
            {directEdges?.map((edge: any, idx: number) => {
              const targetNodeId = edge.source === selectedNode.id ? edge.target : edge.source;
              const targetNode = nodes.find((n: any) => n.id === targetNodeId);
              return (
                <div 
                  key={idx} 
                  onClick={() => onNodeClick(targetNode)}
                  className="p-2.5 bg-slate-950/60 hover:bg-slate-900 border border-slate-850 rounded-xl flex items-center justify-between text-[10px] cursor-pointer transition-colors"
                >
                  <div className="flex flex-col min-w-0">
                    <span className="font-semibold text-slate-200 truncate">{targetNode?.label}</span>
                    <span className="text-[8px] text-slate-500 mt-0.5">{edge.relation}</span>
                  </div>
                  <span className="text-[9px] font-bold text-blue-400 font-mono">{edge.weight}%</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* M1.10 Potential Links */}
        <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800 relative overflow-hidden">
          <span className="text-[9px] text-slate-400 block uppercase font-bold mb-2 flex items-center gap-1">
            <Link2 className="h-3 w-3 text-fuchsia-500" /> Suggested Links (M1.10)
          </span>
          {loadingAnalytics ? (
            <div className="text-[10px] text-slate-500 animate-pulse">Calculating structure...</div>
          ) : potentialLinks.length > 0 ? (
            <div className="space-y-2 relative z-10 max-h-[160px] overflow-y-auto pr-1">
              <div className="text-[8px] text-slate-400 mb-2 italic">Based strictly on shared graph topology. Not confirmed criminal activity.</div>
              {potentialLinks.map((link: any, idx: number) => {
                const targetNode = nodes.find((n: any) => n.id === link.target_entity_id);
                return (
                  <div key={idx} 
                    onClick={() => targetNode && onNodeClick(targetNode)}
                    className="bg-slate-950 hover:bg-slate-900 border-l-2 border-fuchsia-500 p-2 rounded relative cursor-pointer transition-colors border-y border-r border-y-slate-800 border-r-slate-800">
                    <div className="flex justify-between items-start">
                      <span className="text-[10px] font-bold text-fuchsia-400 truncate pr-2">{link.target_entity_name}</span>
                      <span className="text-[8px] px-1 py-0.5 bg-fuchsia-950 text-fuchsia-300 rounded border border-fuchsia-900/50">Score: {link.score.toFixed(2)}</span>
                    </div>
                    {link.explanation && (
                      <div className="mt-2 text-[9px] bg-slate-900/50 p-1.5 rounded border border-slate-800">
                        <span className="text-slate-400 font-bold block mb-1 uppercase text-[8px]">Structural Evidence</span>
                        <p className="text-slate-300 italic leading-tight">{link.explanation.reason}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-[10px] text-slate-500 italic py-1 text-center bg-slate-950/40 rounded border border-slate-800/50">
              No strong structural link candidates found.
            </div>
          )}
        </div>

        {/* M1.12 Source Evidence */}
        <div className="bg-slate-900/50 p-2.5 rounded-lg border border-slate-800 relative overflow-hidden">
          <span className="text-[9px] text-slate-400 block uppercase font-bold mb-2 flex items-center gap-1">
            <Info className="h-3 w-3 text-emerald-500" /> Source Evidence (M1.12)
          </span>
          {loadingAnalytics ? (
            <div className="text-[10px] text-slate-500 animate-pulse">Retrieving provenance...</div>
          ) : evidence.length > 0 ? (
            <div className="space-y-2 relative z-10 max-h-[160px] overflow-y-auto pr-1">
              {evidence.map((ev: any, idx: number) => (
                <div key={idx} className="bg-slate-950 border-l-2 border-emerald-500 p-2 rounded relative">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] font-bold text-emerald-400 truncate pr-2">{ev.title}</span>
                    <span className="text-[8px] px-1 py-0.5 bg-emerald-950 text-emerald-300 rounded border border-emerald-900/50 uppercase">{ev.type}</span>
                  </div>
                  {ev.description && (
                    <p className="text-[9px] text-slate-400 mt-1 leading-tight">{ev.description}</p>
                  )}
                  {ev.provenance && (
                    <div className="mt-1.5 bg-slate-900/50 p-1.5 rounded border border-slate-800 text-[8px]">
                      <span className="text-slate-500 font-bold block mb-0.5 uppercase">Provenance Data</span>
                      <div className="grid grid-cols-2 gap-1 text-slate-300 font-mono">
                        <span>Job: {ev.provenance.ingestion_job_id.substring(0,8)}...</span>
                        <span>File: {ev.provenance.file_name}</span>
                        {ev.provenance.page !== null && <span>Page: {ev.provenance.page}</span>}
                        {ev.provenance.row !== null && <span>Row: {ev.provenance.row}</span>}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
             <div className="text-[10px] text-slate-500 italic py-1 text-center bg-slate-950/40 rounded border border-slate-800/50">
              No direct source evidence recorded.
            </div>
          )}
        </div>

        <div className="p-3 bg-blue-950/15 border border-blue-900/30 rounded-xl space-y-1.5 mt-auto">
          <span className="text-[9px] font-bold text-blue-400 uppercase flex items-center gap-1">
            <Info className="h-3.5 w-3.5" />
            <span>Security clearance statement</span>
          </span>
          <p className="text-[10px] text-slate-400 leading-normal">
            Linkages calculated via cell tower overlap signatures, co-arrest history, and direct phone transaction logs.
          </p>
        </div>
        
        <button 
          onClick={() => {
            const query = `Analyze suspect relationships and connections for ${selectedNode.label}`;
            router.push(`/ai-assistant?query=${encodeURIComponent(query)}`);
          }}
          className="w-full py-2.5 bg-slate-950 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 rounded-xl text-xs font-bold text-slate-300 hover:text-white transition-all text-center"
        >
          Examine Relations via AI
        </button>
      </motion.div>
    </AnimatePresence>
  );
}
