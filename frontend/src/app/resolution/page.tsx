"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { ResolutionReviewResponse, ResolutionService } from "@/services/resolution.service";
import { CheckCircle, PlusCircle, AlertCircle, FileText, Shield, XCircle, Search } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";

export default function EntityResolutionPage() {
  const [queue, setQueue] = useState<ResolutionReviewResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Modal State
  const [activeModal, setActiveModal] = useState<"CONFIRM" | "CREATE" | "REJECT" | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<ResolutionReviewResponse | null>(null);
  const [selectedMatchId, setSelectedMatchId] = useState<string | null>(null);
  const [newEntityName, setNewEntityName] = useState<string>("");

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

  const openConfirmModal = (cand: ResolutionReviewResponse, matchId: string) => {
    setSelectedCandidate(cand);
    setSelectedMatchId(matchId);
    setActiveModal("CONFIRM");
  };

  const openCreateModal = (cand: ResolutionReviewResponse) => {
    setSelectedCandidate(cand);
    setNewEntityName(cand.normalized_value || cand.raw_text);
    setActiveModal("CREATE");
  };

  const openRejectModal = (cand: ResolutionReviewResponse) => {
    setSelectedCandidate(cand);
    setActiveModal("REJECT");
  };

  const closeModal = () => {
    setActiveModal(null);
    setSelectedCandidate(null);
    setSelectedMatchId(null);
    setNewEntityName("");
  };

  const handleConfirm = async () => {
    if (!selectedCandidate || !selectedMatchId) return;
    setSubmitting(true);
    try {
      await ResolutionService.confirmMatch(selectedCandidate.candidate_id, selectedMatchId);
      setQueue((q) => q.filter((c) => c.candidate_id !== selectedCandidate.candidate_id));
      closeModal();
    } catch (err) {
      console.error("Confirmation failed", err);
      setError("Failed to confirm match.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateNew = async () => {
    if (!selectedCandidate || !newEntityName.trim()) return;
    setSubmitting(true);
    try {
      await ResolutionService.createNewEntity(selectedCandidate.candidate_id, newEntityName);
      setQueue((q) => q.filter((c) => c.candidate_id !== selectedCandidate.candidate_id));
      closeModal();
    } catch (err) {
      console.error("Create new failed", err);
      setError("Failed to create new entity.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!selectedCandidate) return;
    setSubmitting(true);
    try {
      await ResolutionService.rejectMatch(selectedCandidate.candidate_id);
      setQueue((q) => q.filter((c) => c.candidate_id !== selectedCandidate.candidate_id));
      closeModal();
    } catch (err) {
      console.error("Reject failed", err);
      setError("Failed to reject match.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6 relative">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[#F5F5F5] flex items-center gap-3">
              <AlertCircle className="w-7 h-7 text-amber-500" />
              Entity Resolution Review
            </h1>
            <p className="text-[#9A9A9A] mt-1">Review candidates that require investigator confirmation.</p>
          </div>
          <div className="bg-[#080808] px-4 py-2 rounded-lg border border-[#222222]">
            <span className="text-[#9A9A9A] text-sm">Pending Reviews: </span>
            <span className="text-white font-bold">{queue.length}</span>
          </div>
        </header>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg flex justify-between items-center">
            {error}
            <button onClick={() => setError("")} className="text-red-200 hover:text-white">✕</button>
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
              description="No entities currently require manual resolution."
            />
          </div>
        ) : (
          <div className="grid gap-6">
            {queue.map((cand) => (
              <div
                key={cand.candidate_id}
                className="bg-[#080808] border border-[#222222] rounded-xl p-6 flex flex-col gap-4"
              >
                {/* Header Information */}
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <span className="px-2 py-1 bg-[#0D0D0D] text-xs font-semibold rounded text-[#F5F5F5] tracking-wider uppercase border border-[#2A2A2A]">
                      {cand.entity_type}
                    </span>
                    <span className="px-2 py-1 bg-amber-900/20 text-amber-500 text-xs font-semibold rounded border border-amber-900/50 tracking-wider">
                      REVIEW REQUIRED
                    </span>
                  </div>
                  <span className="text-sm text-[#666666] flex items-center gap-1">
                    <FileText className="w-4 h-4" />
                    Source: {cand.source_info}
                  </span>
                </div>

                {/* Candidate Information */}
                <div className="bg-[#050505] p-5 rounded-lg border border-[#222222]">
                  <div className="text-xs text-[#666666] mb-1 uppercase tracking-wider">Candidate Extracted</div>
                  <div className="text-2xl font-bold text-white break-words">
                    {cand.raw_text}
                  </div>
                  {cand.normalized_value && cand.normalized_value !== cand.raw_text && (
                    <div className="text-sm text-[#9A9A9A] mt-1 font-mono">
                      normalized: {cand.normalized_value}
                    </div>
                  )}
                </div>

                {/* Possible Matches */}
                <div className="mt-2">
                  <div className="text-sm text-[#9A9A9A] mb-3 flex items-center gap-2">
                    <Search className="w-4 h-4" /> Possible Canonical Matches
                  </div>
                  
                  {cand.possible_matches && cand.possible_matches.length > 0 ? (
                    <div className="flex flex-col gap-3">
                      {cand.possible_matches.map((match) => (
                        <div key={match.canonical_entity_id} className="flex flex-col sm:flex-row items-center justify-between p-4 rounded-lg border border-[#222222] bg-[#0A0A0A] hover:bg-[#0D0D0D] transition-colors">
                          <div>
                            <div className="text-lg font-medium text-amber-400">{match.name}</div>
                            <div className="text-xs text-[#666666] mt-1">Match score: {match.match_score.toFixed(2)}</div>
                          </div>
                          <button
                            onClick={() => openConfirmModal(cand, match.canonical_entity_id)}
                            className="mt-3 sm:mt-0 flex items-center justify-center gap-2 px-5 py-2 bg-amber-600/10 hover:bg-amber-600/20 text-amber-500 border border-amber-600/30 rounded-lg transition-colors text-sm font-medium"
                          >
                            <CheckCircle className="w-4 h-4" />
                            Confirm Match
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-[#666666] p-4 border border-[#222222] rounded-lg bg-[#0A0A0A]">
                      No canonical matches found.
                    </div>
                  )}
                </div>

                {/* Global Actions */}
                <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-[#222222]">
                  <button
                    onClick={() => openCreateModal(cand)}
                    className="flex items-center justify-center gap-2 px-5 py-2 bg-[#0D0D0D] hover:bg-[#111111] text-[#F5F5F5] font-medium rounded-lg transition-colors border border-[#2A2A2A] text-sm"
                  >
                    <PlusCircle className="w-4 h-4" />
                    Create New Entity
                  </button>
                  <button
                    onClick={() => openRejectModal(cand)}
                    className="flex items-center justify-center gap-2 px-5 py-2 bg-[#0D0D0D] hover:bg-red-900/20 text-red-400 font-medium rounded-lg transition-colors border border-[#2A2A2A] hover:border-red-900/50 text-sm"
                  >
                    <XCircle className="w-4 h-4" />
                    Reject Match
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modals */}
        {activeModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <div className="bg-[#0A0A0A] border border-[#222222] rounded-xl shadow-2xl max-w-md w-full overflow-hidden flex flex-col">
              
              {/* Confirm Modal */}
              {activeModal === "CONFIRM" && (
                <>
                  <div className="p-6 border-b border-[#222222]">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <CheckCircle className="w-6 h-6 text-amber-500" />
                      Confirm Match
                    </h3>
                  </div>
                  <div className="p-6 text-[#A0A0A0] space-y-4">
                    <p>Confirm this candidate as the selected canonical entity?</p>
                    <div className="bg-[#050505] p-3 rounded border border-[#222222]">
                      <div className="text-xs text-[#666] mb-1">Candidate</div>
                      <div className="text-white font-medium">{selectedCandidate?.raw_text}</div>
                    </div>
                    <div className="bg-[#050505] p-3 rounded border border-[#222222]">
                      <div className="text-xs text-[#666] mb-1">Selected Canonical Entity</div>
                      <div className="text-amber-400 font-medium">
                        {selectedCandidate?.possible_matches?.find(m => m.canonical_entity_id === selectedMatchId)?.name}
                      </div>
                    </div>
                  </div>
                  <div className="p-4 border-t border-[#222222] flex justify-end gap-3 bg-[#080808]">
                    <button onClick={closeModal} disabled={submitting} className="px-4 py-2 text-[#9A9A9A] hover:text-white transition-colors">Cancel</button>
                    <button onClick={handleConfirm} disabled={submitting} className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded font-medium disabled:opacity-50">
                      {submitting ? 'Submitting...' : 'Confirm Match'}
                    </button>
                  </div>
                </>
              )}

              {/* Create Modal */}
              {activeModal === "CREATE" && (
                <>
                  <div className="p-6 border-b border-[#222222]">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <PlusCircle className="w-6 h-6 text-amber-500" />
                      Create New Entity
                    </h3>
                  </div>
                  <div className="p-6 text-[#A0A0A0] space-y-4">
                    <p>Create a new canonical entity from this candidate.</p>
                    <div>
                      <label className="block text-xs text-[#666] mb-1 uppercase">Entity Name</label>
                      <input 
                        type="text" 
                        value={newEntityName} 
                        onChange={(e) => setNewEntityName(e.target.value)}
                        className="w-full bg-[#050505] border border-[#333] text-white rounded p-3 focus:outline-none focus:border-amber-500"
                        placeholder="Enter entity name..."
                      />
                    </div>
                    <div className="text-xs text-[#666]">
                      Type: <span className="text-white font-medium">{selectedCandidate?.entity_type}</span>
                    </div>
                  </div>
                  <div className="p-4 border-t border-[#222222] flex justify-end gap-3 bg-[#080808]">
                    <button onClick={closeModal} disabled={submitting} className="px-4 py-2 text-[#9A9A9A] hover:text-white transition-colors">Cancel</button>
                    <button onClick={handleCreateNew} disabled={submitting || !newEntityName.trim()} className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded font-medium disabled:opacity-50">
                      {submitting ? 'Creating...' : 'Create Entity'}
                    </button>
                  </div>
                </>
              )}

              {/* Reject Modal */}
              {activeModal === "REJECT" && (
                <>
                  <div className="p-6 border-b border-[#222222]">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <XCircle className="w-6 h-6 text-red-500" />
                      Reject Match
                    </h3>
                  </div>
                  <div className="p-6 text-[#A0A0A0] space-y-4">
                    <p>Are you sure you want to reject this candidate match?</p>
                    <p className="text-sm">The candidate will be removed from the review queue and will remain as unlinked evidence.</p>
                    <div className="bg-[#050505] p-3 rounded border border-[#222222]">
                      <div className="text-xs text-[#666] mb-1">Candidate</div>
                      <div className="text-white font-medium">{selectedCandidate?.raw_text}</div>
                    </div>
                  </div>
                  <div className="p-4 border-t border-[#222222] flex justify-end gap-3 bg-[#080808]">
                    <button onClick={closeModal} disabled={submitting} className="px-4 py-2 text-[#9A9A9A] hover:text-white transition-colors">Cancel</button>
                    <button onClick={handleReject} disabled={submitting} className="px-5 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-medium disabled:opacity-50">
                      {submitting ? 'Rejecting...' : 'Reject Match'}
                    </button>
                  </div>
                </>
              )}

            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
