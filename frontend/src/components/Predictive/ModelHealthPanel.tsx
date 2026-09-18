"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { Activity, TrendingUp, TrendingDown, Minus } from "lucide-react";

const TrendIcon = ({ trend }: { trend: string }) => {
  if (trend === "Degrading") return <TrendingDown className="h-3 w-3 text-rose-500" />;
  if (trend === "Improving") return <TrendingUp className="h-3 w-3 text-emerald-500" />;
  return <Minus className="h-3 w-3 text-[#666666]" />;
};

export default function ModelHealthPanel() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    apiClient.get("/model-monitoring/summary")
      .then(r => r.data)
      .then(res => setData(res))
      .catch(console.warn);
  }, []);

  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  if (data.status === "insufficient_data") {
    return (
      <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex items-center justify-center">
        <p className="text-amber-500 text-xs font-mono">Insufficient Historical Data for Monitoring</p>
      </div>
    );
  }

  const fm = data.forecast_monitoring;
  const hm = data.hotspot_monitoring;

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <Activity className="h-4 w-4 text-emerald-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Model Health</h3>
      </div>
      
      <div className="flex-1 p-4 grid grid-cols-2 gap-3">
         <div className="bg-[#050505] border border-[#222222] rounded p-3">
            <h4 className="text-[10px] text-[#666666] uppercase tracking-widest mb-1 flex justify-between">
              Forecast MAPE <TrendIcon trend={fm.trend} />
            </h4>
            <div className={`text-xl font-black ${fm.trend === 'Degrading' ? 'text-rose-500' : 'text-emerald-500'}`}>
              {fm.mape.toFixed(1)}%
            </div>
         </div>
         <div className="bg-[#050505] border border-[#222222] rounded p-3">
            <h4 className="text-[10px] text-[#666666] uppercase tracking-widest mb-1 flex justify-between">
              Hotspot F1 <TrendIcon trend={hm.trend} />
            </h4>
            <div className={`text-xl font-black ${hm.trend === 'Degrading' ? 'text-rose-500' : 'text-emerald-500'}`}>
              {hm.f1_score.toFixed(2)}
            </div>
         </div>
      </div>
    </div>
  );
}
