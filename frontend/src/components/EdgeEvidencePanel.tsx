"use client";
import React from "react";
import { X, Link2, FileText, BarChart2, MapPin, Briefcase } from "lucide-react";

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
    desc?: string;
  } | null;
  onClose: () => void;
}

export default function EdgeEvidencePanel({ edge, onClose }: EdgeEvidencePanelProps) {
  if (!edge) return null;

  const confidencePct = edge.confidence != null
    ? Math.round(edge.confidence * 100)
    : null;

  const confidenceColor =
    confidencePct != null && confidencePct >= 80
      ? "text-emerald-400"
      : confidencePct != null && confidencePct >= 60
      ? "text-amber-400"
      : "text-red-400";

  // Prevent placeholder "REL_TYPE (Conf: 0.95)" string from being displayed as evidence
  const isFallbackDesc = edge.desc && /^[A-Z_]+\s*\(Conf:\s*[\d\.]+\)$/.test(edge.desc.trim());
  const displayEvidence = edge.evidence_text || (!isFallbackDesc ? edge.desc : null);

  return (
    <div className="absolute top-4 right-4 z-20 w-80 bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl backdrop-blur-md p-4 space-y-3">
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
          className="text-slate-500 hover:text-slate-300 transition-colors"
          aria-label="Close evidence panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Relationship type */}
      <div className="bg-blue-950/50 border border-blue-800/40 rounded-lg px-3 py-2">
        <span className="text-[9px] text-blue-400/70 font-semibold uppercase tracking-widest block">Type</span>
        <p className="text-blue-300 font-mono font-bold text-sm tracking-wider">
          {edge.relation}
        </p>
      </div>

      {/* Source Evidence snippet */}
      {displayEvidence ? (
        <div className="bg-slate-800/60 border border-emerald-800/40 rounded-lg p-2.5 space-y-1.5">
          <div className="flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-[10px] text-emerald-400 uppercase tracking-wider font-bold">
              Source Evidence
            </span>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed italic border-l-2 border-emerald-500/50 pl-2">
            &ldquo;{displayEvidence}&rdquo;
          </p>
        </div>
      ) : (
        <div className="bg-slate-800/30 border border-slate-700/30 rounded-lg p-2">
          <p className="text-[10px] text-slate-500 italic">No direct source quote recorded.</p>
        </div>
      )}

      {/* Metadata section */}
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
            <span className={`font-bold ${confidenceColor}`}>
              {confidencePct}%
            </span>
          </div>
        )}

        {/* Extraction method */}
        {edge.extraction_method && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-slate-500" /> Method
            </span>
            <span className="text-slate-300 font-mono text-[11px]">{edge.extraction_method}</span>
          </div>
        )}

        {/* Source page */}
        {edge.source_page != null && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-500" /> Source Page
            </span>
            <span className="text-slate-200 font-mono font-semibold">{edge.source_page}</span>
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
