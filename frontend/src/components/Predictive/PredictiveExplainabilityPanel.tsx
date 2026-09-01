"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { ScanSearch, AlertTriangle } from "lucide-react";
import ConfidenceBreakdown from "./ConfidenceBreakdown";
import EvidenceExplorer from "./EvidenceExplorer";

export default function PredictiveExplainabilityPanel() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/predictive-explainability/summary")
      .then(r => r.data)
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-full bg-slate-900 border border-slate-800 rounded-xl animate-pulse"></div>;

  const isInsufficient = data?.status === "insufficient_data";
  
  // Extract a representative explainer for the dashboard preview (e.g. Forecast)
  const expPreview = data?.forecast_explainability?.explainability;

  return (
    <div className="h-full bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800 bg-slate-950/50 flex items-center gap-2">
        <ScanSearch className="h-4 w-4 text-blue-500" />
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Explainability Engine</h3>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto relative">
        {isInsufficient || !expPreview ? (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-50" />
            <h4 className="text-sm font-bold text-amber-500 mb-1">Insufficient Data for Explainability</h4>
            <p className="text-xs text-slate-400 font-mono">Cannot compute confidence on missing baselines.</p>
          </div>
        ) : (
          <div className="h-full flex flex-col">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-3">Model Preview: Crime Forecaster</p>
            <ConfidenceBreakdown 
               score={expPreview.confidence_score} 
               level={expPreview.confidence_level} 
            />
            <EvidenceExplorer 
               evidence={expPreview.evidence} 
               riskDrivers={expPreview.risk_drivers} 
            />
          </div>
        )}
      </div>
    </div>
  );
}
