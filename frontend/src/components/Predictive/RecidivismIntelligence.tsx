"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { UserMinus, AlertTriangle } from "lucide-react";

export default function RecidivismIntelligence() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Testing with a dummy ID, expecting insufficient data or error in empty db
    apiClient.get("/predictive/offenders/00000000-0000-0000-0000-000000000000")
      .then(r => r.data)
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const isInsufficient = data?.status === "insufficient_data" || data?.status === "error";

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex items-center gap-2">
        <UserMinus className="h-4 w-4 text-rose-500" />
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest">Recidivism Risk (Sample)</h3>
      </div>
      
      <div className="flex-1 p-4 flex flex-col justify-center relative">
        {isInsufficient ? (
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-50" />
            <h4 className="text-sm font-bold text-amber-500 mb-1">Target Not Found / Insufficient Data</h4>
            <p className="text-xs text-[#9A9A9A] font-mono mb-2">{data.message}</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <span className="text-xs text-[#9A9A9A] font-bold uppercase tracking-widest">Reoffend Probability</span>
              <span className="text-2xl font-black text-rose-500">{(data?.probability * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-[#9A9A9A] font-bold uppercase tracking-widest">Risk Classification</span>
              <span className={`text-xs font-mono px-2 py-0.5 rounded border ${data?.risk_level === 'HIGH' ? 'text-rose-500 bg-rose-500/10 border-rose-500/20' : 'text-amber-500 bg-amber-500/10 border-amber-500/20'}`}>
                {data?.risk_level}
              </span>
            </div>
            <div className="mt-2 pt-2 border-t border-[#222222]">
              <span className="block text-[10px] text-[#666666] uppercase tracking-widest mb-2">Algorithm Evidence</span>
              <ul className="text-[10px] text-[#9A9A9A] font-mono space-y-1 list-disc pl-4">
                {data?.evidence?.map((ev: string, i: number) => <li key={i}>{ev}</li>)}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
