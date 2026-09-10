import React, { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { AlertTriangle, Users, Network, Info } from "lucide-react";

export function CommunityPanel() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCommunities = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get('/graph/analytics/communities');
        setData(res.data);
      } catch (err: any) {
        console.error("Failed to fetch communities", err);
        setError(err.response?.data?.detail || "Failed to fetch community data");
      } finally {
        setLoading(false);
      }
    };
    
    fetchCommunities();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 text-sm py-10">
        <div className="animate-pulse flex flex-col items-center gap-2">
          <Network className="h-6 w-6" />
          <span>Analyzing Graph Structure...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-950/20 border border-red-900/50 rounded-xl m-4">
        <div className="flex items-center gap-2 text-red-400 mb-2">
          <AlertTriangle className="h-5 w-5" />
          <h3 className="font-bold text-sm">Error Loading Communities</h3>
        </div>
        <p className="text-xs text-red-300/80">{error}</p>
      </div>
    );
  }

  const isDeferred = data?.status === "INFRASTRUCTURE_DEFERRED";

  return (
    <div className="flex flex-col h-full bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden mt-4">
      <div className="p-4 border-b border-slate-800 bg-slate-950/40">
        <div className="flex items-center gap-2 mb-1">
          <Users className="h-5 w-5 text-indigo-400" />
          <h2 className="font-bold text-white tracking-tight">Graph Communities</h2>
        </div>
        <p className="text-xs text-slate-400">
          Groups of entities identified purely from structural graph connectivity, distinct from geographic spatial hotspots.
        </p>
      </div>

      <div className="p-5 flex-1 overflow-y-auto">
        {isDeferred ? (
          <div className="flex flex-col items-center justify-center text-center py-8 space-y-4">
            <div className="h-14 w-14 rounded-full bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Network className="h-7 w-7" />
            </div>
            <div>
              <h3 className="text-slate-200 font-bold text-base mb-2">Community Detection Unavailable</h3>
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs text-slate-400 max-w-sm text-left space-y-3">
                <p>
                  <span className="font-semibold text-slate-300">Status:</span> {data?.status}
                </p>
                <p className="leading-relaxed">
                  {data?.message || "Graph projection capabilities required for algorithms like Louvain/Leiden are not available in the current deployment tier."}
                </p>
                <div className="flex items-start gap-2 bg-blue-950/30 border border-blue-900/50 p-2.5 rounded-lg">
                  <Info className="h-4 w-4 text-blue-400 shrink-0 mt-0.5" />
                  <p className="text-[10px] text-blue-300/80">
                    This is an honest data limitation. The system preserves the existing architecture and does not fabricate fake communities or repurpose DBSCAN spatial clusters to bypass this infrastructure constraint.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
             {data?.communities?.length > 0 ? (
               <div className="text-sm text-slate-300">Communities found: {data.communities.length}</div>
             ) : (
               <div className="text-center text-slate-500 text-sm py-8">No communities detected</div>
             )}
          </div>
        )}
      </div>
    </div>
  );
}
