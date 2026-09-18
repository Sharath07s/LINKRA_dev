"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { TrendingUp, Activity, CheckCircle, AlertTriangle } from "lucide-react";

export default function ForecastOverview() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // We fetch forecast for a hardcoded district for the sake of the widget, 
  // or default to an empty string if we had a global endpoint.
  // In a real scenario we'd use a district selector context.
  // For the demo we simulate fetching the first district.
  
  useEffect(() => {
    apiClient.get("/predictive/forecast?district_id=00000000-0000-0000-0000-000000000000") // This will likely hit insufficient data
      .then(r => r.data)
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const isInsufficient = data?.status === "insufficient_data";

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-emerald-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">30-Day Volume Forecast</h3>
      </div>
      
      <div className="flex-1 p-4 flex flex-col justify-center relative">
        {isInsufficient ? (
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-50" />
            <h4 className="text-sm font-bold text-amber-500 mb-1">Insufficient Historical Data</h4>
            <p className="text-xs text-[#9A9A9A] font-mono mb-2">{data.message}</p>
            <div className="inline-flex items-center gap-2 text-[10px] bg-[#050505] px-2 py-1 rounded border border-[#222222]">
              <span className="text-[#666666]">Records Required: {data.required_records}</span>
              <span className="text-[#666666]">|</span>
              <span className="text-amber-500">Available: {data.available_records}</span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <span className="text-xs text-[#9A9A9A] font-bold uppercase tracking-widest">Predicted Volume</span>
              <span className="text-2xl font-black text-white">{data?.predicted_count}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-[#9A9A9A] font-bold uppercase tracking-widest">Trend</span>
              <span className={`text-xs font-mono px-2 py-0.5 rounded border ${data?.trend === 'increasing' ? 'text-amber-500 bg-amber-500/10 border-amber-500/20' : 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20'}`}>
                {data?.trend?.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-[#9A9A9A] font-bold uppercase tracking-widest">Confidence Score</span>
              <span className="text-sm font-mono text-[#10B981]">{(data?.confidence * 100).toFixed(0)}%</span>
            </div>
            {data?.evidence && (
              <div className="mt-2 pt-2 border-t border-[#222222] text-[10px] text-[#666666] font-mono">
                {data.evidence[0]}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
