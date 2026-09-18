"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { AlertCircle, Zap } from "lucide-react";

export default function EmergingThreats() {
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchThreats = async () => {
      try {
        const res = await apiClient.get(`/executive/emerging-threats`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch emerging threats:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchThreats();
  }, []);

  if (isLoading) return <div suppressHydrationWarning className="h-full bg-[#080808]/40 border border-[#222222] rounded-2xl animate-pulse"></div>;

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-amber-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">Emerging Threats</h3>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
          </span>
          <span className="text-[9px] text-amber-500 font-bold uppercase tracking-widest">Live Monitor</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {data?.map((threat, idx) => (
          <div key={idx} className="bg-[#050505]/60 border border-[#222222] p-3 rounded-xl border-l-2 hover:bg-[#0D0D0D]/50 transition-colors" 
               style={{ borderLeftColor: threat.severity === 'CRITICAL' ? '#ef4444' : threat.severity === 'HIGH' ? '#f59e0b' : '#3b82f6' }}>
            <div className="flex justify-between items-start mb-1">
              <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                {threat.severity === 'CRITICAL' && <AlertCircle className="h-3 w-3 text-red-500" />}
                {threat.type}
              </h4>
              <span className="text-[9px] font-mono text-[#666666]">{new Date(threat.detected_at).toLocaleTimeString()}</span>
            </div>
            <div className="flex justify-between items-end mt-2">
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#9A9A9A]">{threat.district}</span>
              <span className="text-[9px] font-bold bg-[#0D0D0D] text-[#F5F5F5] px-1.5 py-0.5 rounded">
                {threat.confidence}% Conf
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
