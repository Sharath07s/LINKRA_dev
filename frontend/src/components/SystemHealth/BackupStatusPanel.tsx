import { apiClient } from "@/lib/api-client";
import React, { useState } from "react";
import { DatabaseBackup, Play } from "lucide-react";

export default function BackupStatusPanel({ data }: { data: any }) {
  const [triggering, setTriggering] = useState(false);

  if (!data) return <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] animate-pulse"></div>;

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      await apiClient.post("/infrastructure/backups/trigger");
      // In a real app we'd refresh the data here or rely on the realtime stream
    } catch (_) {}
    setTimeout(() => setTriggering(false), 2000);
  };

  return (
    <div className="h-full bg-[#080808]/50 rounded-xl border border-[#222222] p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <DatabaseBackup className="h-4 w-4 text-amber-400" />
          Backup Status
        </h3>
        <span className={`text-[10px] font-mono px-2 py-1 rounded border ${data.status === 'operational' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'}`}>
          {data.status === 'operational' ? 'READY' : 'UNAVAILABLE'}
        </span>
      </div>

      <div className="flex-1 flex flex-col gap-2">
        <div className="flex justify-between items-center text-xs font-mono">
          <span className="text-[#666666]">PostgreSQL Backup:</span>
          <span className={data.postgres_ready ? "text-emerald-400" : "text-red-400"}>{data.postgres_ready ? "Available" : "Missing Tool"}</span>
        </div>
        <div className="flex justify-between items-center text-xs font-mono">
          <span className="text-[#666666]">Neo4j Backup:</span>
          <span className={data.neo4j_ready ? "text-emerald-400" : "text-red-400"}>{data.neo4j_ready ? "Available" : "Missing Tool"}</span>
        </div>
        
        <div className="mt-auto">
          <button 
            onClick={handleTrigger}
            disabled={triggering || data.status !== 'operational'}
            className="w-full bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs py-2 rounded flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            <Play className="h-3 w-3" />
            {triggering ? "TRIGGERING..." : "MANUAL BACKUP"}
          </button>
        </div>
      </div>
    </div>
  );
}
