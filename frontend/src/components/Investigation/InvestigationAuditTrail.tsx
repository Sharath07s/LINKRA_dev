"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { List, CheckCircle2, Eye, Download, Search, Settings } from "lucide-react";

interface AuditLog {
  id: string;
  action: string;
  module: string;
  timestamp: string;
}

interface AuditTrailProps {
  investigationId: string;
}

export default function InvestigationAuditTrail({ investigationId }: AuditTrailProps) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAudit = async () => {
      try {
        const res = await apiClient.get(`/investigations/${investigationId}/audit`);
        if (res.status === 200) {
          const data = res.data;
          setLogs(data);
        }
      } catch (err) {
        console.warn("Failed to fetch audit logs", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (investigationId) fetchAudit();
  }, [investigationId]);

  const getActionIcon = (action: string) => {
    if (action.includes("View")) return <Eye className="h-3.5 w-3.5 text-blue-400" />;
    if (action.includes("Generate") || action.includes("Export")) return <Download className="h-3.5 w-3.5 text-emerald-400" />;
    if (action.includes("Query") || action.includes("Search")) return <Search className="h-3.5 w-3.5 text-amber-400" />;
    if (action.includes("Opened") || action.includes("Assign")) return <CheckCircle2 className="h-3.5 w-3.5 text-purple-400" />;
    return <Settings className="h-3.5 w-3.5 text-slate-400" />;
  };

  return (
    <div suppressHydrationWarning className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex items-center gap-2">
        <List className="h-4 w-4 text-slate-400" />
        <h3 className="text-sm font-bold text-white tracking-wide">Secure Audit Trail</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <div className="flex h-full items-center justify-center text-xs text-slate-500 font-bold uppercase tracking-widest animate-pulse">
            Syncing Ledger...
          </div>
        ) : (
          <div className="space-y-1">
            {logs?.map((log) => (
              <div key={log.id} className="flex items-center gap-3 p-3 hover:bg-slate-800/50 rounded-xl group transition-colors">
                <div className="h-7 w-7 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-center shrink-0">
                  {getActionIcon(log.action)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline mb-0.5">
                    <span className="text-xs font-semibold text-slate-200 truncate pr-2">{log.action}</span>
                    <span className="text-[9px] text-slate-500 font-mono shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{log.module}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
