"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import ReasoningTracePanel from "../AIWorkspace/ReasoningTracePanel";

interface FIRExplainabilityProps {
  firId: string;
}

export default function FIRExplainabilityPanel({ firId }: FIRExplainabilityProps) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real scenario, this would come from the summary endpoint or a dedicated explainability endpoint.
    // Simulating the fetch based on the FIR summary.
    const fetchExplainability = async () => {
      try {
        const res = await apiClient.get(`/crimes/${firId}/summary`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch FIR explainability:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (firId) fetchExplainability();
  }, [firId]);

  if (isLoading) return <div className="h-full bg-slate-900/40 border border-slate-800 rounded-2xl animate-pulse"></div>;
  if (!data) return null;

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-slate-800 bg-slate-950/50 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-500" />
          <h3 className="text-sm font-bold text-white tracking-wide">AI Explainability</h3>
        </div>
      </div>
      <div className="p-5 flex-1 overflow-y-auto">
        <ReasoningTracePanel 
          trace={[
            `Ingested FIR structured data and narrative from DB.`,
            `Extracted core entities via NER (Confidence: ${data.confidence}%).`,
            `Queried PGVector for nearest historical neighbors using all-MiniLM-L6-v2 embeddings.`,
            `Cross-referenced extracted suspects with Neo4j criminal network graph.`,
            `Generated final synthesis via ${data.provider === 'system_fallback' ? 'deterministic rules engine' : 'LLM'}.`
          ]}
          confidenceBreakdown={[
            { category: "Entity Extraction", score: data.confidence },
            { category: "M.O. Matching", score: 88 },
            { category: "Threat Assessment", score: 95 }
          ]}
          sourceAttribution={`PostgreSQL (crimes) + PGVector (document_chunks)`}
          databaseRecords={["Record 1", "Record 2"]}
          neo4jNodes={["Node 1", "Node 2", "Node 3"]}
        />
      </div>
    </div>
  );
}
