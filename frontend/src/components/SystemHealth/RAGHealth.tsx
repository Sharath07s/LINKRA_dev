"use client";

import React from "react";
import { Search, CheckCircle, AlertTriangle } from "lucide-react";

export default function RAGHealth({ data }: { data: any }) {
  if (!data) return <div className="h-full bg-[#080808] border border-[#222222] rounded-xl animate-pulse"></div>;

  const isHealthy = data.status === "healthy";

  return (
    <div className="h-full bg-[#080808] border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <Search className="h-4 w-4 text-emerald-500" /> RAG & Vector Engine
        </h3>
        {isHealthy ? <CheckCircle className="h-4 w-4 text-emerald-500" /> : <AlertTriangle className="h-4 w-4 text-amber-500" />}
      </div>
      
      <div className="flex-1 p-3 flex flex-col justify-center gap-3">
        <div className="bg-[#050505] rounded p-2 border border-[#222222]">
          <span className="block text-[10px] text-[#666666] uppercase tracking-widest mb-1">Embedding Model</span>
          <span className="text-xs font-mono text-emerald-400">{data.embedding_model}</span>
        </div>
        
        <div className="space-y-2 mt-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-[#9A9A9A]">Document Chunks</span>
            <span className="font-mono text-[#F5F5F5] bg-[#0D0D0D] px-2 py-0.5 rounded">{data.chunk_count}</span>
          </div>
          <div className="flex justify-between items-center text-xs">
            <span className="text-[#9A9A9A]">Vector Embeddings (pgvector)</span>
            <span className="font-mono text-[#F5F5F5] bg-[#0D0D0D] px-2 py-0.5 rounded">{data.vector_count}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
