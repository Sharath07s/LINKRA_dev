"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Users, AlertTriangle } from "lucide-react";

export default function HighRiskOffenders() {
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchOffenders = async () => {
      try {
        const res = await apiClient.get(`/executive/high-risk-offenders`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch high risk offenders:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchOffenders();
  }, []);

  if (isLoading) return <div className="h-full bg-[#080808]/40 border border-[#222222] rounded-2xl animate-pulse"></div>;

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-red-400" />
          <h3 className="text-sm font-bold text-white tracking-wide">High Risk Offenders</h3>
        </div>
        <span className="text-[9px] bg-red-900/30 text-red-400 border border-red-800/50 px-2 py-0.5 rounded font-mono uppercase">
          SQL + Neo4j
        </span>
      </div>
      
      <div className="flex-1 overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#050505]/80 border-b border-[#222222] text-[10px] font-bold text-[#666666] uppercase tracking-widest">
              <th className="p-3 pl-4">Name</th>
              <th className="p-3">Risk Score</th>
              <th className="p-3">District</th>
              <th className="p-3">Linked Crimes</th>
              <th className="p-3">Network Size</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((offender, idx) => (
              <tr key={idx} className="border-b border-[#222222]/50 hover:bg-[#0D0D0D]/20 transition-colors">
                <td className="p-3 pl-4 text-xs font-bold text-[#F5F5F5]">
                  <div className="flex items-center gap-2">
                    {offender.threat_level === 'CRITICAL' && <AlertTriangle className="h-3 w-3 text-red-500" />}
                    {offender.name}
                  </div>
                </td>
                <td className="p-3">
                  <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${offender.risk_score >= 90 ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                    {offender.risk_score}
                  </span>
                </td>
                <td className="p-3 text-[10px] font-bold uppercase tracking-widest text-[#9A9A9A]">{offender.district}</td>
                <td className="p-3 text-xs font-medium text-[#9A9A9A]">{offender.crimes}</td>
                <td className="p-3 text-xs font-medium text-[#9A9A9A]">{offender.network_size}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
