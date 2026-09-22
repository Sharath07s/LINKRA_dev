"use client";
import React, { useState, useEffect } from "react";
import {
  X,
  Link2,
  FileText,
  BarChart2,
  MapPin,
  Briefcase,
  Loader2,
  AlertCircle,
  BookOpen,
} from "lucide-react";
import {
  relationshipService,
  RelationshipEvidenceResponse,
  EvidenceLink,
} from "@/services/relationship.service";

interface EdgeEvidencePanelProps {
  edge: {
    id?: string;
    relation: string;
    source?: string;
    target?: string;
    confidence?: number;
    extraction_method?: string;
    source_page?: number | null;
    source_row?: number | null;
    ingestion_job_id?: string | null;
    evidence_text?: string | null;
    status?: string;
    desc?: string;
  } | null;
  onClose: () => void;
}

type FetchState = "idle" | "loading" | "success" | "error" | "no_id";

export default function EdgeEvidencePanel({ edge, onClose }: EdgeEvidencePanelProps) {
  const [evidenceData, setEvidenceData] = useState<RelationshipEvidenceResponse | null>(null);
  const [fetchState, setFetchState] = useState<FetchState>("idle");

  useEffect(() => {
    // Reset state whenever the selected edge changes
    setEvidenceData(null);

    if (!edge) {
      setFetchState("idle");
      return;
    }

    if (!edge.id) {
      // Edge exists but has no ID — cannot call the Evidence API
      setFetchState("no_id");
      return;
    }

    let cancelled = false;
    setFetchState("loading");

    relationshipService
      .getRelationshipEvidence(edge.id)
      .then((data) => {
        if (!cancelled) {
          setEvidenceData(data);
          setFetchState("success");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setFetchState("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [edge?.id]);

  if (!edge) return null;

  const confidencePct =
    edge.confidence != null ? Math.round(edge.confidence * 100) : null;

  const confidenceColor =
    confidencePct != null && confidencePct >= 80
      ? "text-emerald-400"
      : confidencePct != null && confidencePct >= 60
      ? "text-amber-400"
      : "text-red-400";

  // Prevent placeholder "REL_TYPE (Conf: 0.95)" string from being displayed as evidence
  const isFallbackDesc =
    edge.desc && /^[A-Z_]+\s*\(Conf:\s*[\d\.]+\)$/.test(edge.desc.trim());
  const displayEvidence = edge.evidence_text || (!isFallbackDesc ? edge.desc : null);

  return (
    <div className="absolute top-4 right-4 z-20 w-80 bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl backdrop-blur-md p-4 space-y-3 max-h-[85vh] overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link2 className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Relationship Details
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-[#666666] hover:text-[#F5F5F5] transition-colors"
          aria-label="Close evidence panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Relationship type */}
      <div className="bg-blue-950/50 border border-blue-800/40 rounded-lg px-3 py-2">
        <span className="text-[9px] text-blue-400/70 font-semibold uppercase tracking-widest block">
          Type
        </span>
        <p className="text-blue-300 font-mono font-bold text-sm tracking-wider">
          {edge.relation}
        </p>
      </div>

      {/* Intelligence Status */}
      <div className={`border rounded-lg px-3 py-2 ${
        edge.status === 'PREDICTED' 
          ? 'bg-purple-950/50 border-purple-800/40' 
          : edge.status === 'INFERRED' 
            ? 'bg-orange-950/50 border-orange-800/40' 
            : 'bg-emerald-950/50 border-emerald-800/40'
      }`}>
        <span className={`text-[9px] font-semibold uppercase tracking-widest block ${
          edge.status === 'PREDICTED' 
            ? 'text-purple-400/70' 
            : edge.status === 'INFERRED' 
              ? 'text-orange-400/70' 
              : 'text-emerald-400/70'
        }`}>
          Intelligence Status
        </span>
        <p className={`font-mono font-bold text-sm tracking-wider ${
          edge.status === 'PREDICTED' 
            ? 'text-purple-300' 
            : edge.status === 'INFERRED' 
              ? 'text-orange-300' 
              : 'text-emerald-300'
        }`}>
          {edge.status || 'CONFIRMED'}
        </p>
      </div>

      {/* ── DOCUMENT CHUNK EVIDENCE (from EvidenceLink API) ── */}
      <div className="space-y-2">
        <div className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-violet-400" />
          <span className="text-[10px] text-violet-400 uppercase tracking-wider font-bold">
            Document Evidence
          </span>
        </div>

        {/* Loading state */}
        {fetchState === "loading" && (
          <div className="bg-slate-800/40 border border-slate-700/40 rounded-lg p-3 flex items-center gap-2">
            <Loader2 className="w-3.5 h-3.5 text-slate-400 animate-spin" />
            <span className="text-[11px] text-slate-400">Loading evidence…</span>
          </div>
        )}

        {/* Error state */}
        {fetchState === "error" && (
          <div className="bg-red-950/30 border border-red-800/40 rounded-lg p-2.5 flex items-center gap-2">
            <AlertCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
            <span className="text-[11px] text-red-300">
              Could not load evidence from API.
            </span>
          </div>
        )}

        {/* No relationship ID — cannot call API */}
        {fetchState === "no_id" && (
          <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-2">
            <p className="text-[10px] text-slate-500 italic">
              No relationship ID — document evidence unavailable.
            </p>
          </div>
        )}

        {/* Success: render each EvidenceLink */}
        {fetchState === "success" && evidenceData && (
          <>
            {evidenceData.evidence_links.length === 0 ? (
              <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-2">
                <p className="text-[10px] text-slate-500 italic">
                  No document evidence found for this relationship.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {evidenceData.evidence_links.map((link: EvidenceLink, idx: number) => (
                  <div
                    key={link.evidence_link_id}
                    className="bg-slate-800/60 border border-violet-800/30 rounded-lg p-2.5 space-y-1.5"
                  >
                    {/* Chunk quote */}
                    {link.quote_snippet && (
                      <p className="text-xs text-slate-200 leading-relaxed italic border-l-2 border-violet-500/50 pl-2">
                        &ldquo;{link.quote_snippet}&rdquo;
                      </p>
                    )}

                    {/* Provenance row */}
                    <div className="flex flex-wrap gap-x-3 gap-y-1 pt-0.5">
                      {/* Source filename */}
                      {link.source_filename && (
                        <span className="flex items-center gap-1 text-[10px] text-slate-400">
                          <FileText className="w-3 h-3 text-slate-500" />
                          <span
                            className="font-mono text-slate-300 truncate max-w-[140px]"
                            title={link.source_filename}
                          >
                            {link.source_filename}
                          </span>
                        </span>
                      )}

                      {/* Page number */}
                      {link.page_number != null && (
                        <span className="flex items-center gap-1 text-[10px] text-slate-400">
                          <MapPin className="w-3 h-3 text-slate-500" />
                          <span className="font-mono text-slate-300">
                            p.{link.page_number}
                          </span>
                        </span>
                      )}

                      {/* Char offsets */}
                      {link.char_start != null && link.char_end != null && (
                        <span className="text-[9px] text-slate-500 font-mono">
                          [{link.char_start}–{link.char_end}]
                        </span>
                      )}
                    </div>

                    {/* Link-level confidence badge */}
                    {link.confidence != null && (
                      <div className="flex justify-end">
                        <span className="text-[9px] font-bold text-violet-300 bg-violet-900/40 border border-violet-700/40 px-1.5 py-0.5 rounded">
                          {Math.round(link.confidence * 100)}% conf
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Top-level source_filename from job (fallback when no links have it) */}
            {evidenceData.evidence_links.length > 0 &&
              evidenceData.source_filename &&
              !evidenceData.evidence_links.some((l) => l.source_filename) && (
                <div className="text-[9px] text-slate-500 font-mono flex items-center gap-1">
                  <FileText className="w-3 h-3" />
                  {evidenceData.source_filename}
                </div>
              )}
          </>
        )}
      </div>

      {/* ── NEO4J RELATIONSHIP-LEVEL EVIDENCE TEXT (retained) ── */}
      {displayEvidence && (
        <div className="bg-slate-800/60 border border-emerald-800/40 rounded-lg p-2.5 space-y-1.5">
          <div className="flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-[10px] text-emerald-400 uppercase tracking-wider font-bold">
              Extraction Snippet
            </span>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed italic border-l-2 border-emerald-500/50 pl-2">
            &ldquo;{displayEvidence}&rdquo;
          </p>
        </div>
      )}

      {/* ── METADATA ── */}
      <div className="bg-slate-950/40 border border-slate-800/60 rounded-lg p-2.5 space-y-2">
        <span className="text-[9px] text-slate-500 uppercase tracking-widest font-bold block">
          Extraction Metadata
        </span>

        {/* Confidence */}
        {confidencePct != null && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <BarChart2 className="w-3.5 h-3.5 text-slate-500" /> Confidence
            </span>
            <span className={`font-bold ${confidenceColor}`}>{confidencePct}%</span>
          </div>
        )}

        {/* Extraction method */}
        {edge.extraction_method && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-slate-500" /> Method
            </span>
            <span className="text-slate-300 font-mono text-[11px]">
              {edge.extraction_method}
            </span>
          </div>
        )}

        {/* Source page */}
        {edge.source_page != null && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-500" /> Source Page
            </span>
            <span className="text-slate-200 font-mono font-semibold">
              {edge.source_page}
            </span>
          </div>
        )}

        {/* Ingestion job */}
        {edge.ingestion_job_id && (
          <div className="pt-1 border-t border-slate-800/60 text-[9px] text-slate-500 font-mono truncate">
            Job: {edge.ingestion_job_id}
          </div>
        )}
      </div>
    </div>
  );
}
