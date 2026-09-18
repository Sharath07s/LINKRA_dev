"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Link2, Network } from "lucide-react";

interface RelatedFIRsProps {
  firId: string;
}

export default function RelatedFIRsPanel({ firId }: RelatedFIRsProps) {
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSimilar = async () => {
      try {
        const res = await apiClient.get(`/crimes/${firId}/similar`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch similar FIRs:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (firId) fetchSimilar();
  }, [firId]);

  if (isLoading) return <div className="h-full bg-[#080808]/40 border border-[#222222] rounded-2xl animate-pulse"></div>;

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <h3 className="text-sm font-bold text-white tracking-wide">Semantic Case Matches</h3>
        <span className="text-[9px] bg-blue-900/30 text-[#10B981] border border-blue-800/50 px-2 py-0.5 rounded font-mono uppercase">
          PGVector
        </span>
      </div>
      <div className="p-4 flex-1 overflow-y-auto space-y-3">
        {data.length === 0 ? (
          <div className="text-xs text-[#666666] font-medium text-center py-4">No similar records found in vector space.</div>
        ) : (
          data?.map((fir, idx) => (
            <div key={idx} className="bg-[#050505]/60 border border-[#222222] p-3 rounded-xl hover:border-[#10B981]/50 transition-colors cursor-pointer group">
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-xs font-bold text-[#F5F5F5] group-hover:text-[#10B981] transition-colors flex items-center gap-1.5">
                  <Link2 className="h-3 w-3" /> {fir.fir_number}
                </span>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                  {fir.similarity_score.toFixed(1)}% Match
                </span>
              </div>
              <div className="flex flex-wrap gap-2 text-[10px] text-[#9A9A9A] font-medium">
                <span>{fir.district}</span>
                <span>•</span>
                <span>{fir.crime_type}</span>
              </div>
              {fir.linked_network && (
                <div className="mt-2 pt-2 border-t border-[#222222] flex items-center gap-1.5">
                  <Network className="h-3 w-3 text-purple-400" />
                  <span className="text-[10px] text-purple-300 font-bold uppercase tracking-wider">{fir.linked_network}</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
