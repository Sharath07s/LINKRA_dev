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
    ingestion_job_id?: string | null;
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

  return (
    <div className="absolute top-4 right-4 z-20 w-72 bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl backdrop-blur-md p-4 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link2 className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Relationship
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
        <p className="text-blue-300 font-mono font-bold text-sm tracking-wider">
          {edge.relation}
        </p>
      </div>

      {/* Confidence */}
      {confidencePct != null && (
        <div className="flex items-center gap-2">
          <BarChart2 className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-400">Confidence:</span>
          <span className={`text-xs font-bold ${confidenceColor}`}>
            {confidencePct}%
          </span>
        </div>
      )}

      {/* Extraction method */}
      {edge.extraction_method && (
        <div className="flex items-center gap-2">
          <Briefcase className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-400">Method:</span>
          <span className="text-xs text-slate-300 font-mono">{edge.extraction_method}</span>
        </div>
      )}

      {/* Source page */}
      {edge.source_page != null && (
        <div className="flex items-center gap-2">
          <MapPin className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-400">Source Page:</span>
          <span className="text-xs text-slate-300">{edge.source_page}</span>
        </div>
      )}

      {/* Edge desc / evidence snippet */}
      {edge.desc && (
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-lg p-2.5 space-y-1">
          <div className="flex items-center gap-1.5">
            <FileText className="w-3 h-3 text-slate-400" />
            <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">
              Evidence
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed italic">
            &ldquo;{edge.desc}&rdquo;
          </p>
        </div>
      )}

      {/* Ingestion job */}
      {edge.ingestion_job_id && (
        <p className="text-[10px] text-slate-600 font-mono truncate">
          Job: {edge.ingestion_job_id}
        </p>
      )}
    </div>
  );
}
