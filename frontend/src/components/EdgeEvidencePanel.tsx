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
    <div className="absolute top-4 right-4 z-20 w-72 bg-[#080808]/95 border border-[#2A2A2A] rounded-xl shadow-2xl backdrop-blur-md p-4 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link2 className="w-4 h-4 text-[#10B981]" />
          <span className="text-xs font-bold text-[#F5F5F5] uppercase tracking-wider">
            Relationship
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
        <p className="text-[#10B981] font-mono font-bold text-sm tracking-wider">
          {edge.relation}
        </p>
      </div>

      {/* Confidence */}
      {confidencePct != null && (
        <div className="flex items-center gap-2">
          <BarChart2 className="w-3.5 h-3.5 text-[#9A9A9A]" />
          <span className="text-xs text-[#9A9A9A]">Confidence:</span>
          <span className={`text-xs font-bold ${confidenceColor}`}>
            {confidencePct}%
          </span>
        </div>
      )}

      {/* Extraction method */}
      {edge.extraction_method && (
        <div className="flex items-center gap-2">
          <Briefcase className="w-3.5 h-3.5 text-[#9A9A9A]" />
          <span className="text-xs text-[#9A9A9A]">Method:</span>
          <span className="text-xs text-[#F5F5F5] font-mono">{edge.extraction_method}</span>
        </div>
      )}

      {/* Source page */}
      {edge.source_page != null && (
        <div className="flex items-center gap-2">
          <MapPin className="w-3.5 h-3.5 text-[#9A9A9A]" />
          <span className="text-xs text-[#9A9A9A]">Source Page:</span>
          <span className="text-xs text-[#F5F5F5]">{edge.source_page}</span>
        </div>
      )}

      {/* Edge desc / evidence snippet */}
      {edge.desc && (
        <div className="bg-[#0D0D0D]/60 border border-[#2A2A2A]/50 rounded-lg p-2.5 space-y-1">
          <div className="flex items-center gap-1.5">
            <FileText className="w-3 h-3 text-[#9A9A9A]" />
            <span className="text-[10px] text-[#666666] uppercase tracking-wider font-semibold">
              Evidence
            </span>
          </div>
          <p className="text-xs text-[#F5F5F5] leading-relaxed italic">
            &ldquo;{edge.desc}&rdquo;
          </p>
        </div>
      )}

      {/* Ingestion job */}
      {edge.ingestion_job_id && (
        <p className="text-[10px] text-[#666666] font-mono truncate">
          Job: {edge.ingestion_job_id}
        </p>
      )}
    </div>
  );
}
