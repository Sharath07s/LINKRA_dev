"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { ResolutionReviewResponse, ResolutionService } from "@/services/resolution.service";
import { CheckCircle, PlusCircle, AlertCircle, FileText, Shield } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";

export default function EntityResolutionPage() {
  const [queue, setQueue] = useState<ResolutionReviewResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadQueue = async () => {
    try {
      setLoading(true);
      const data = await ResolutionService.getReviewQueue(0, 50);
      setQueue(data);
    } catch (err) {
      setError("Failed to load review queue.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleApprove = async (id: string) => {
    try {
      await ResolutionService.approveMatch(id);
      setQueue((q) => q.filter((c) => c.candidate_id !== id));
    } catch (err) {
      console.error("Approval failed", err);
    }
  };

  const handleCreateNew = async (id: string) => {
    try {
      await ResolutionService.createNewEntity(id);
      setQueue((q) => q.filter((c) => c.candidate_id !== id));
    } catch (err) {
      console.error("Create new failed", err);
    }
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[#F5F5F5] flex items-center gap-3">
              <AlertCircle className="w-7 h-7 text-amber-500" />
              Entity Resolution
            </h1>
            <p className="text-[#9A9A9A] mt-1">Review ambiguous entity extractions and merge them with existing canonical entities or create new identities.</p>
          </div>
          <div className="bg-[#080808] px-4 py-2 rounded-lg border border-[#222222]">
            <span className="text-[#9A9A9A] text-sm">Pending Reviews: </span>
            <span className="text-white font-bold">{queue.length}</span>
          </div>
        </header>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
          </div>
        ) : queue.length === 0 ? (
          <div className="bg-[#080808] border border-[#222222] rounded-xl p-8">
            <EmptyState
              icon={<Shield className="h-10 w-10 text-[#666666]" />}
              title="Resolution Queue Empty"
              description="No entities currently require manual resolution. The automated matching engine is running."
            />
          </div>
        ) : (
          <div className="grid gap-4">
            {queue.map((cand) => (
              <div
                key={cand.candidate_id}
                className="bg-[#080808] border border-[#222222] rounded-xl p-6 flex flex-col md:flex-row gap-6 items-start md:items-center hover:border-[#2A2A2A] transition-colors"
              >
                <div className="flex-1 space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="px-2 py-1 bg-[#0D0D0D] text-xs font-semibold rounded text-[#F5F5F5] tracking-wider">
                      {cand.entity_type}
                    </span>
                    <span className="text-sm text-[#666666] flex items-center gap-1">
                      <FileText className="w-4 h-4" />
                      {cand.source_info}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
                    <div className="bg-[#050505] p-4 rounded-lg border border-[#222222]">
                      <div className="text-xs text-[#666666] mb-1">Extracted Candidate</div>
                      <div className="text-lg font-medium text-white break-words">
                        {cand.raw_text}
                      </div>
                      {cand.normalized_value && cand.normalized_value !== cand.raw_text && (
                        <div className="text-sm text-[#9A9A9A] mt-1">
                          Norm: {cand.normalized_value}
                        </div>
                      )}
                    </div>

                    <div className="hidden md:flex items-center justify-center">
                      <div className="w-full h-[1px] bg-[#0D0D0D] relative">
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-[#080808] px-3 py-1 rounded-full text-xs text-amber-500 border border-[#2A2A2A]">
                          {(cand.resolution_score !== null)
                            ? `${(cand.resolution_score * 100).toFixed(0)}% Match`
                            : 'Unknown Match'}
                        </div>
                      </div>
                    </div>

                    <div className="bg-amber-950/20 p-4 rounded-lg border border-amber-900/50">
                      <div className="text-xs text-amber-500/70 mb-1">Proposed Canonical Entity</div>
                      <div className="text-lg font-medium text-amber-400 break-words">
                        {cand.proposed_canonical_name || "Unknown Entity"}
                      </div>
                      <div className="text-xs text-[#666666] mt-2 font-mono truncate">
                        ID: {cand.proposed_canonical_id}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-3 w-full md:w-auto">
                  <button
                    onClick={() => handleApprove(cand.candidate_id)}
                    className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white font-medium rounded-lg transition-colors shadow-[0_0_15px_rgba(217,119,6,0.3)] hover:shadow-[0_0_20px_rgba(217,119,6,0.5)]"
                  >
                    <CheckCircle className="w-5 h-5" />
                    Approve Merge
                  </button>
                  <button
                    onClick={() => handleCreateNew(cand.candidate_id)}
                    className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-[#0D0D0D] hover:bg-[#111111] text-[#F5F5F5] font-medium rounded-lg transition-colors border border-[#2A2A2A]"
                  >
                    <PlusCircle className="w-5 h-5" />
                    Create New
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
