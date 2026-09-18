"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Map } from "lucide-react";

export default function DistrictRankings() {
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchRankings = async () => {
      try {
        const res = await apiClient.get(`/executive/district-rankings`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch district rankings:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchRankings();
  }, []);

  if (isLoading) return <div className="h-full bg-[#080808]/40 border border-[#222222] rounded-2xl animate-pulse"></div>;

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Map className="h-4 w-4 text-[#10B981]" />
          <h3 className="text-sm font-bold text-white tracking-wide">District Intelligence Ranking</h3>
        </div>
        <span className="text-[9px] bg-blue-900/30 text-[#10B981] border border-blue-800/50 px-2 py-0.5 rounded font-mono uppercase">
          Live Data
        </span>
      </div>
      
      <div className="flex-1 overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#050505]/80 border-b border-[#222222] text-[10px] font-bold text-[#666666] uppercase tracking-widest">
              <th className="p-3 pl-4">District</th>
              <th className="p-3">Threat Score</th>
              <th className="p-3">Growth</th>
              <th className="p-3">Hotspots</th>
              <th className="p-3">Networks</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((district, idx) => (
              <tr key={idx} className="border-b border-[#222222]/50 hover:bg-[#0D0D0D]/20 transition-colors">
                <td className="p-3 pl-4 text-xs font-bold text-[#F5F5F5]">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-[#666666] font-mono w-4">{idx + 1}.</span>
                    {district.district}
                  </div>
                </td>
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-[#0D0D0D] rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${district.score > 80 ? 'bg-red-500' : district.score > 60 ? 'bg-amber-500' : 'bg-emerald-500'}`} 
                        style={{ width: `${district.score}%` }} 
                      />
                    </div>
                    <span className="text-xs font-mono font-bold text-white">{district.score}</span>
                  </div>
                </td>
                <td className="p-3">
                  <div className={`flex items-center gap-1 text-xs font-bold ${district.trend === 'up' ? 'text-red-400' : 'text-emerald-400'}`}>
                    {district.trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {district.growth}
                  </div>
                </td>
                <td className="p-3 text-xs font-medium text-[#9A9A9A]">{district.hotspots}</td>
                <td className="p-3 text-xs font-medium text-[#9A9A9A]">{district.networks}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
