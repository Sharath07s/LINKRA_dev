"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { CheckCircle, AlertTriangle, BarChart, ShieldCheck } from "lucide-react";

export default function ValidationMetrics() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/predictive-validation/summary")
      .then(r => r.data)
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-full bg-slate-900 border border-slate-800 rounded-xl animate-pulse"></div>;

  const isInsufficient = data?.status === "insufficient_data";

  return (
    <div className="h-full bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800 bg-slate-950/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-500" />
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Predictive Validation Layer</h3>
        </div>
        {!isInsufficient && (
          <span className="text-[10px] font-mono text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1">
            <CheckCircle className="h-3 w-3" /> VALIDATED
          </span>
        )}
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto relative">
        {isInsufficient ? (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-50" />
            <h4 className="text-sm font-bold text-amber-500 mb-1">Insufficient Historical Data For Validation</h4>
            <div className="inline-flex items-center gap-2 text-[10px] bg-slate-950 px-2 py-1 rounded border border-slate-800">
              <span className="text-slate-500">Required: {data.required_records}</span>
              <span className="text-slate-500">|</span>
              <span className="text-amber-500">Available: {data.available_records}</span>
            </div>
            <p className="text-[10px] text-slate-500 mt-2 font-mono uppercase tracking-widest">({data.module} engine)</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 h-full">
            {/* Forecast Accuracy */}
            <div className="bg-slate-950 border border-slate-800 rounded p-3 flex flex-col justify-between">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-1">
                <BarChart className="h-3 w-3" /> Forecast Model
              </h4>
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">MAPE</span>
                  <span className="text-emerald-400">{data?.forecast_accuracy?.mape}%</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">MAE</span>
                  <span className="text-emerald-400">{data?.forecast_accuracy?.mae}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">RMSE</span>
                  <span className="text-emerald-400">{data?.forecast_accuracy?.rmse}</span>
                </div>
              </div>
            </div>

            {/* Hotspot Accuracy */}
            <div className="bg-slate-950 border border-slate-800 rounded p-3 flex flex-col justify-between">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Spatial Hotspots</h4>
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Precision</span>
                  <span className="text-emerald-400">{data?.hotspot_accuracy?.precision}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Recall</span>
                  <span className="text-emerald-400">{data?.hotspot_accuracy?.recall}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">F1 Score</span>
                  <span className="text-emerald-400">{data?.hotspot_accuracy?.f1_score}</span>
                </div>
              </div>
            </div>

            {/* Recidivism Accuracy */}
            <div className="bg-slate-950 border border-slate-800 rounded p-3 flex flex-col justify-between">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Recidivism Engine</h4>
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Accuracy</span>
                  <span className="text-emerald-400">{data?.recidivism_accuracy?.accuracy}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Precision</span>
                  <span className="text-emerald-400">{data?.recidivism_accuracy?.precision}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">F1 Score</span>
                  <span className="text-emerald-400">{data?.recidivism_accuracy?.f1_score}</span>
                </div>
              </div>
            </div>

            {/* Network Accuracy */}
            <div className="bg-slate-950 border border-slate-800 rounded p-3 flex flex-col justify-between">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Network Growth</h4>
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Accuracy</span>
                  <span className="text-emerald-400">{data?.network_accuracy?.prediction_accuracy}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">Detection Rate</span>
                  <span className="text-emerald-400">{data?.network_accuracy?.expansion_detection_rate}</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">False Exp. Rate</span>
                  <span className="text-amber-500">{data?.network_accuracy?.false_expansion_rate}</span>
                </div>
              </div>
            </div>
            
          </div>
        )}
      </div>
    </div>
  );
}
