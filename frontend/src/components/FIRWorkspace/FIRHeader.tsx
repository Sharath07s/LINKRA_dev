"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { FileText, MapPin, Calendar, AlertTriangle } from "lucide-react";

interface FIRHeaderProps {
  firId: string;
}

export default function FIRHeader({ firId }: FIRHeaderProps) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHeader = async () => {
      try {
        const res = await apiClient.get(`/crimes/${firId}`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch FIR header:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (firId) fetchHeader();
  }, [firId]);

  if (isLoading) return <div suppressHydrationWarning className="h-24 bg-[#080808]/40 border border-[#222222] rounded-2xl animate-pulse"></div>;
  if (!data) return null;

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col md:flex-row justify-between p-5 gap-4 shadow-lg shadow-black/20">
      <div className="flex items-center gap-4">
        <div className="h-12 w-12 rounded-xl bg-blue-900/40 border border-[#10B981]/30 flex items-center justify-center text-[#10B981] shrink-0">
          <FileText className="h-6 w-6" />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-white tracking-tight">{data.fir_number}</h1>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest border ${data.priority === 'CRITICAL' ? 'text-red-400 bg-red-500/10 border-red-500/20' : 'text-amber-400 bg-amber-500/10 border-amber-500/20'}`}>
              {data.priority} PRIORITY
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs font-medium text-[#9A9A9A]">
            <span className="flex items-center gap-1.5"><AlertTriangle className="h-3 w-3 text-red-400" /> {data.crime_type}</span>
            <span className="flex items-center gap-1.5"><MapPin className="h-3 w-3 text-[#666666]" /> {data.station}, {data.district}</span>
            <span className="flex items-center gap-1.5"><Calendar className="h-3 w-3 text-[#666666]" /> {new Date(data.date_registered).toLocaleString()}</span>
          </div>
        </div>
      </div>
      <div className="flex flex-col items-end justify-center gap-1">
        <span className="text-[10px] font-bold text-[#666666] uppercase tracking-widest block">Investigation Status</span>
        <span className="text-sm font-bold text-emerald-400 flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          {data.status}
        </span>
        <span className="text-[10px] text-[#666666] font-mono mt-1">Case ID: {data.case_id}</span>
      </div>
    </div>
  );
}
