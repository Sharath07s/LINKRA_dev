"use client";
import { useState } from "react";
import {
  FileText, Users, Link2, ShieldAlert, TrendingUp, AlertTriangle,
  Sparkles, Download, ChevronDown, ChevronRight, ExternalLink, CheckCircle2
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import ReactMarkdown from "react-markdown";

interface ReportViewProps {
  investigationId: string;
}

const SOURCE_BADGE: Record<string, { label: string; cls: string }> = {
  observed: { label: "OBSERVED", cls: "bg-emerald-900/40 text-emerald-400 border-emerald-700/50" },
  structural_analysis: { label: "STRUCTURAL ANALYSIS", cls: "bg-blue-900/40 text-[#10B981] border-blue-700/50" },
  prediction: { label: "PREDICTION", cls: "bg-amber-900/40 text-amber-400 border-amber-700/50" },
  ai_generated: { label: "AI-GENERATED", cls: "bg-purple-900/40 text-purple-400 border-purple-700/50" },
};

function SourceBadge({ type }: { type: string }) {
  const b = SOURCE_BADGE[type] ?? SOURCE_BADGE["observed"];
  return (
    <span className={`inline-flex items-center text-[8px] font-bold px-1.5 py-0.5 rounded border ${b.cls}`}>
      {b.label}
    </span>
  );
}

function Section({ icon: Icon, title, count, sourceType, children, defaultOpen = false }:
  { icon: any; title: string; count?: number; sourceType: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-[#222222] rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 p-4 bg-[#080808]/60 hover:bg-[#080808] transition-colors text-left"
      >
        <Icon className="h-4 w-4 text-[#9A9A9A] shrink-0" />
        <span className="font-semibold text-sm text-[#F5F5F5] flex-1">{title}</span>
        {count !== undefined && (
          <span className="text-xs font-mono text-[#666666] mr-2">{count}</span>
        )}
        <SourceBadge type={sourceType} />
        {open ? <ChevronDown className="h-3 w-3 text-[#666666] ml-2" /> : <ChevronRight className="h-3 w-3 text-[#666666] ml-2" />}
      </button>
      {open && <div className="p-4 bg-[#050505]/60 space-y-2">{children}</div>}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return <p className="text-xs text-[#666666] italic">{message}</p>;
}

export function ReportView({ investigationId }: ReportViewProps) {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get(`/investigations/${investigationId}/report`);
      setReport(res.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to load report.");
    } finally {
      setLoading(false);
    }
  };

  const generateNarrative = async () => {
    setGenerating(true);
    try {
      const res = await apiClient.post(`/investigations/${investigationId}/report/generate`);
      setReport(res.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to generate AI narrative.");
    } finally {
      setGenerating(false);
    }
  };

  const exportJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `linkra-report-${investigationId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!report && !loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px] gap-4 text-[#9A9A9A]">
        <FileText className="h-12 w-12 text-[#666666]" />
        <div className="text-center">
          <p className="font-semibold text-[#F5F5F5] mb-1">Investigation Report</p>
          <p className="text-xs text-[#666666] max-w-xs">
            Aggregates verified entities, relationships, evidence, graph analytics,
            anomalies, and potential links into a structured report.
          </p>
        </div>
        <button
          onClick={loadReport}
          className="px-5 py-2 bg-[#10B981] hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition-colors"
        >
          Generate Report
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[300px] text-[#666666] text-sm animate-pulse">
        Assembling report from verified intelligence…
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[200px]">
        <p className="text-red-400 text-sm">{error}</p>
      </div>
    );
  }

  const meta = report?.metadata;

  return (
    <div className="space-y-4">
      {/* Header Actions */}
      <div className="flex items-center gap-3 justify-between flex-wrap">
        <div>
          <p className="text-xs text-[#666666]">
            Generated: {meta?.generated_at ? new Date(meta.generated_at).toLocaleString() : "—"}
            {" · "}v{meta?.report_version}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadReport}
            className="px-3 py-1.5 bg-[#0D0D0D] hover:bg-[#111111] border border-[#2A2A2A] text-xs font-semibold text-[#F5F5F5] rounded-lg transition-colors"
          >
            Refresh
          </button>
          <button
            onClick={generateNarrative}
            disabled={generating}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-700/30 hover:bg-purple-700/50 border border-purple-600/40 text-xs font-bold text-purple-300 rounded-lg transition-colors disabled:opacity-50"
          >
            <Sparkles className="h-3 w-3" />
            {generating ? "Generating…" : "AI Narrative"}
          </button>
          <button
            onClick={exportJSON}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0D0D0D] hover:bg-[#111111] border border-[#2A2A2A] text-xs font-semibold text-[#F5F5F5] rounded-lg transition-colors"
          >
            <Download className="h-3 w-3" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Metrics Bar */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
        {[
          { label: "Entities", val: meta?.entity_count, type: "observed" },
          { label: "Relations", val: meta?.relationship_count, type: "observed" },
          { label: "Evidence", val: meta?.evidence_count, type: "observed" },
          { label: "Anomalies", val: meta?.anomaly_count, type: "structural_analysis" },
          { label: "Pot. Links", val: meta?.potential_link_count, type: "prediction" },
          { label: "AI", val: meta?.ai_generated ? "Yes" : "No", type: "ai_generated" },
        ].map(({ label, val, type }) => (
          <div key={label} className="bg-[#080808]/60 border border-[#222222] rounded-lg p-2 text-center">
            <p className="text-[8px] font-bold text-[#666666] uppercase">{label}</p>
            <p className="text-sm font-bold text-[#F5F5F5]">{val ?? "—"}</p>
            <SourceBadge type={type} />
          </div>
        ))}
      </div>

      {/* Sections */}
      <div className="space-y-2">

        {/* Investigation Summary */}
        <Section icon={FileText} title="Investigation Overview" sourceType="observed" defaultOpen>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {[
              ["ID", report.investigation.investigation_id],
              ["Status", report.investigation.status],
              ["Priority", report.investigation.priority],
              ["Crime ID", report.investigation.crime_id],
              ["Started", report.investigation.started_at],
              ["Completed", report.investigation.completed_at],
            ].map(([k, v]) => (
              <div key={k as string}>
                <span className="text-[#666666]">{k}: </span>
                <span className="text-[#F5F5F5]">{(v as string) || "—"}</span>
              </div>
            ))}
          </div>
          {report.investigation.summary && (
            <p className="text-xs text-[#9A9A9A] mt-2 border-t border-[#222222] pt-2">{report.investigation.summary}</p>
          )}
        </Section>

        {/* Entities */}
        <Section icon={Users} title="Verified Entities" count={report.entities.length} sourceType="observed">
          {report.entities.length === 0
            ? <EmptyState message="No entities associated with this investigation." />
            : report.entities.map((e: any) => (
              <div key={e.entity_id} className="bg-[#080808]/40 rounded-lg p-2 text-xs border border-[#222222]">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3 w-3 text-emerald-400 shrink-0" />
                  <span className="font-semibold text-[#F5F5F5]">{e.name}</span>
                  <span className="text-[#666666]">({e.entity_type})</span>
                </div>
                {e.aliases?.length > 0 && (
                  <p className="text-[#666666] mt-0.5">Aliases: {e.aliases.join(", ")}</p>
                )}
              </div>
            ))
          }
        </Section>

        {/* Relationships */}
        <Section icon={Link2} title="Observed Relationships" count={report.relationships.length} sourceType="observed">
          {report.relationships.length === 0
            ? <EmptyState message="No observed relationships found." />
            : report.relationships.map((r: any, i: number) => (
              <div key={i} className="text-xs border border-[#222222] rounded-lg p-2 bg-[#080808]/40">
                <p className="text-[#F5F5F5]">
                  <span className="font-semibold">{r.source_entity_name}</span>
                  <span className="mx-1.5 text-[#10B981]">—{r.relationship_type}→</span>
                  <span className="font-semibold">{r.target_entity_name}</span>
                </p>
                <p className="text-[#666666] mt-0.5">
                  Confidence: {(r.confidence * 100).toFixed(0)}% · {r.extraction_method}
                  {r.provenance?.file_name && ` · Source: ${r.provenance.file_name}`}
                </p>
              </div>
            ))
          }
        </Section>

        {/* Evidence */}
        <Section icon={FileText} title="Source Evidence" count={report.evidence.length} sourceType="observed">
          {report.evidence.length === 0
            ? <EmptyState message="No source evidence available." />
            : report.evidence.slice(0, 20).map((ev: any, i: number) => (
              <div key={i} className="text-xs border-l-2 border-emerald-700 pl-2 py-0.5">
                <p className="text-[#F5F5F5] font-medium">{ev.title}</p>
                <p className="text-[#666666]">{ev.description}</p>
                {ev.provenance && (
                  <p className="text-[#666666]">{ev.provenance.file_name} — {ev.provenance.source_type}</p>
                )}
              </div>
            ))
          }
          {report.evidence.length > 20 && (
            <p className="text-xs text-[#666666] italic">+{report.evidence.length - 20} more evidence records</p>
          )}
        </Section>

        {/* Graph Analytics */}
        <Section icon={TrendingUp} title="Graph Structure (Structural Analytics)" count={report.graph_summary.entity_summaries.length} sourceType="structural_analysis">
          {report.graph_summary.entity_summaries.length === 0
            ? <EmptyState message="No graph analytics available." />
            : report.graph_summary.entity_summaries.map((gs: any) => (
              <div key={gs.entity_id} className="text-xs border border-[#222222] rounded-lg p-2 bg-[#080808]/40">
                <p className="font-semibold text-[#F5F5F5]">{gs.entity_name}</p>
                <p className="text-[#666666]">Degree: {gs.degree} (In: {gs.in_degree}, Out: {gs.out_degree})</p>
              </div>
            ))
          }
        </Section>

        {/* Anomalies */}
        <Section icon={AlertTriangle} title="Structural Anomalies" count={report.anomalies.length} sourceType="structural_analysis">
          {report.anomalies.length === 0
            ? <EmptyState message="No structural anomalies detected." />
            : report.anomalies.map((a: any) => (
              <div key={a.anomaly_id} className="text-xs border border-[#222222] rounded-lg p-3 bg-[#080808]/40">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="h-3 w-3 text-amber-400" />
                  <span className="font-semibold text-[#F5F5F5]">{a.entity_name}</span>
                  <span className={`text-[8px] font-bold px-1 py-0.5 rounded ${
                    a.severity === "HIGH" ? "bg-red-900/40 text-red-400" :
                    a.severity === "MEDIUM" ? "bg-amber-900/40 text-amber-400" :
                    "bg-[#0D0D0D] text-[#9A9A9A]"
                  }`}>{a.severity}</span>
                </div>
                <p className="text-[#9A9A9A]">{a.reason}</p>
                <p className="text-[#666666] text-[9px] mt-1 italic">{a.disclaimer}</p>
              </div>
            ))
          }
        </Section>

        {/* Potential Links */}
        <Section icon={ShieldAlert} title="Potential Links (Topology-Based Predictions)" count={report.potential_links.length} sourceType="prediction">
          {report.potential_links.length === 0
            ? <EmptyState message="No strong structural link candidates found." />
            : report.potential_links.map((pl: any, i: number) => (
              <div key={i} className="text-xs border border-amber-900/40 rounded-lg p-3 bg-amber-950/20">
                <div className="flex items-center gap-2 mb-1">
                  <ExternalLink className="h-3 w-3 text-amber-400" />
                  <span className="font-semibold text-[#F5F5F5]">{pl.source_entity_name}</span>
                  <span className="text-[#666666] mx-1">↔</span>
                  <span className="font-semibold text-[#F5F5F5]">{pl.target_entity_name}</span>
                  <span className="ml-auto font-mono text-amber-400">{pl.score.toFixed(2)}</span>
                </div>
                <p className="text-[#9A9A9A]">{pl.reason}</p>
                <p className="text-[9px] text-[#666666]">
                  Common neighbors: {pl.common_neighbors} · Jaccard: {pl.jaccard_similarity.toFixed(3)}
                </p>
                <p className="text-amber-600/80 text-[9px] mt-1 italic">{pl.disclaimer}</p>
              </div>
            ))
          }
        </Section>

        {/* AI Narrative */}
        {report.ai_section && (
          <Section icon={Sparkles} title="AI-Assisted Assessment" sourceType="ai_generated" defaultOpen>
            <div className="text-xs text-purple-300/80 italic border border-purple-900/40 rounded-lg p-2 bg-purple-950/20 mb-3">
              <strong>⚠ Disclaimer:</strong> {report.ai_section.disclaimer}
            </div>
            <div className="prose prose-invert prose-xs max-w-none text-[#F5F5F5]">
              <ReactMarkdown>{report.ai_section.narrative}</ReactMarkdown>
            </div>
            <p className="text-[9px] text-[#666666] mt-2">Provider: {report.ai_section.provider}</p>
          </Section>
        )}

        {/* Limitations */}
        {report.limitations?.length > 0 && (
          <div className="border border-[#222222] rounded-xl p-4 bg-[#080808]/40">
            <p className="text-xs font-bold text-[#9A9A9A] uppercase mb-2">Limitations & Missing Data</p>
            <ul className="space-y-1">
              {report.limitations.map((lim: string, i: number) => (
                <li key={i} className="text-xs text-[#666666] flex items-start gap-1.5">
                  <span className="text-[#666666] mt-0.5">—</span>
                  {lim}
                </li>
              ))}
            </ul>
          </div>
        )}

      </div>
    </div>
  );
}
