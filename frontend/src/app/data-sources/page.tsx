"use client";

import { useState, useCallback } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import {
  UploadCloud,
  FileText,
  CheckCircle,
  XCircle,
  Loader2,
  ChevronDown,
  ChevronRight,
  User,
  MapPin,
  Phone,
  Car,
  Calendar,
  Building,
  RefreshCw,
  AlertCircle,
  Database,
} from "lucide-react";
import {
  ingestionService,
  SOURCE_TYPES,
  type IngestionJob,
  type IngestionJobDetail,
  type EntityCandidate,
} from "@/services/ingestion.service";

// ── Entity type icon/color mapping ─────────────────────────────────────
const ENTITY_CONFIG: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  PERSON: { icon: <User className="h-3.5 w-3.5" />, color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/20" },
  ORGANIZATION: { icon: <Building className="h-3.5 w-3.5" />, color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/20" },
  LOCATION: { icon: <MapPin className="h-3.5 w-3.5" />, color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20" },
  PHONE: { icon: <Phone className="h-3.5 w-3.5" />, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20" },
  VEHICLE: { icon: <Car className="h-3.5 w-3.5" />, color: "text-rose-400", bg: "bg-rose-500/10 border-rose-500/20" },
  DATE: { icon: <Calendar className="h-3.5 w-3.5" />, color: "text-cyan-400", bg: "bg-cyan-500/10 border-cyan-500/20" },
};

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  QUEUED: { label: "Queued", color: "text-slate-400", icon: <Loader2 className="h-3.5 w-3.5 animate-spin" /> },
  PROCESSING: { label: "Processing", color: "text-blue-400", icon: <Loader2 className="h-3.5 w-3.5 animate-spin" /> },
  PARSED: { label: "Parsed", color: "text-amber-400", icon: <Loader2 className="h-3.5 w-3.5 animate-spin" /> },
  EXTRACTED: { label: "Extracting", color: "text-indigo-400", icon: <Loader2 className="h-3.5 w-3.5 animate-spin" /> },
  COMPLETED: { label: "Completed", color: "text-emerald-400", icon: <CheckCircle className="h-3.5 w-3.5" /> },
  FAILED: { label: "Failed", color: "text-red-400", icon: <XCircle className="h-3.5 w-3.5" /> },
};

export default function DataSourcesPage() {
  // Upload form state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [sourceType, setSourceType] = useState("OTHER");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Jobs list state
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  // Detail panel state
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);
  const [jobDetail, setJobDetail] = useState<IngestionJobDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  // Drag state
  const [isDragging, setIsDragging] = useState(false);

  // ── Load jobs ────────────────────────────────────────────────────────
  const loadJobs = useCallback(async () => {
    setIsLoadingJobs(true);
    try {
      const data = await ingestionService.listJobs();
      setJobs(data);
      setHasLoaded(true);
    } catch (err: any) {
      console.error("Failed to load ingestion jobs:", err);
    } finally {
      setIsLoadingJobs(false);
    }
  }, []);

  // Load on first render
  if (!hasLoaded && !isLoadingJobs) {
    loadJobs();
  }

  // ── Upload handler ───────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setUploadError(null);
    try {
      await ingestionService.uploadFile(selectedFile, sourceType);
      setSelectedFile(null);
      await loadJobs();
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || "Upload failed.";
      setUploadError(typeof detail === "string" ? detail : JSON.stringify(detail));
    } finally {
      setIsUploading(false);
    }
  };

  // ── Expand job detail ────────────────────────────────────────────────
  const toggleJobDetail = async (jobId: string) => {
    if (expandedJobId === jobId) {
      setExpandedJobId(null);
      setJobDetail(null);
      return;
    }
    setExpandedJobId(jobId);
    setIsLoadingDetail(true);
    try {
      const detail = await ingestionService.getJobDetail(jobId);
      setJobDetail(detail);
    } catch (err) {
      console.error("Failed to load job detail:", err);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  // ── Drag and drop handlers ──────────────────────────────────────────
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) setSelectedFile(file);
  };

  // ── Group entities by type ──────────────────────────────────────────
  const groupEntities = (entities: EntityCandidate[]) => {
    const groups: Record<string, EntityCandidate[]> = {};
    for (const ent of entities) {
      if (!groups[ent.entity_type]) groups[ent.entity_type] = [];
      groups[ent.entity_type].push(ent);
    }
    return groups;
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Data Ingestion</h1>
            <p className="text-slate-400 mt-1">Upload and process intelligence source documents.</p>
          </div>
          <button
            onClick={loadJobs}
            disabled={isLoadingJobs}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs font-semibold transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoadingJobs ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Upload Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Upload Zone */}
          <div className="lg:col-span-7">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`relative bg-slate-900/40 border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
                isDragging
                  ? "border-blue-500 bg-blue-500/5"
                  : selectedFile
                  ? "border-emerald-500/40 bg-emerald-500/5"
                  : "border-slate-700 hover:border-slate-600"
              }`}
            >
              {selectedFile ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-center gap-3">
                    <FileText className="h-8 w-8 text-emerald-400" />
                    <div className="text-left">
                      <p className="text-sm font-semibold text-white">{selectedFile.name}</p>
                      <p className="text-[11px] text-slate-400">
                        {(selectedFile.size / 1024).toFixed(1)} KB • {selectedFile.type || "unknown type"}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-[10px] text-slate-500 hover:text-slate-300 uppercase tracking-wider"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <UploadCloud className="h-10 w-10 text-slate-500 mx-auto" />
                  <div>
                    <p className="text-sm font-semibold text-slate-300">Drop files here or click to browse</p>
                    <p className="text-[11px] text-slate-500 mt-1">Supports PDF, CSV, JSON, and TXT files (max 50 MB)</p>
                  </div>
                  <label className="inline-block cursor-pointer">
                    <span className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-semibold transition-colors border border-slate-700">
                      Browse Files
                    </span>
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.csv,.json,.txt"
                      onChange={(e) => {
                        const f = e.target.files?.[0];
                        if (f) setSelectedFile(f);
                      }}
                    />
                  </label>
                </div>
              )}
            </div>
          </div>

          {/* Source Type + Upload Button */}
          <div className="lg:col-span-5 bg-slate-900/40 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h3 className="font-bold text-white text-sm border-b border-slate-800 pb-3">Upload Configuration</h3>

            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Source Type</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {SOURCE_TYPES.map((st) => (
                  <option key={st.value} value={st.value}>{st.label}</option>
                ))}
              </select>
            </div>

            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-blue-500/15 flex items-center justify-center gap-1.5"
            >
              {isUploading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <UploadCloud className="h-3.5 w-3.5" />
                  <span>Upload & Process</span>
                </>
              )}
            </button>

            {uploadError && (
              <div className="p-3 bg-red-950/30 border border-red-900/40 rounded-xl flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-red-400 shrink-0 mt-0.5" />
                <p className="text-[11px] text-red-400 leading-relaxed">{uploadError}</p>
              </div>
            )}

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-start gap-2 text-[9px] text-slate-500">
              <Database className="h-4 w-4 text-slate-600 shrink-0 mt-0.5" />
              <p className="leading-relaxed">
                Uploaded files are parsed, normalized, and processed through the NLP extraction pipeline. Extracted entity candidates are stored with full provenance.
              </p>
            </div>
          </div>
        </div>

        {/* Ingestion Jobs List */}
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6">
          <div className="flex justify-between items-center border-b border-slate-800/80 pb-4 mb-4">
            <div>
              <h3 className="font-bold text-white text-lg">Ingestion Jobs</h3>
              <p className="text-xs text-slate-400">Processed documents and extracted intelligence</p>
            </div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              {jobs.length} {jobs.length === 1 ? "Job" : "Jobs"}
            </span>
          </div>

          {isLoadingJobs && !hasLoaded ? (
            <div className="flex items-center justify-center py-12 gap-2 text-slate-500">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span className="text-sm">Loading ingestion jobs...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <UploadCloud className="h-10 w-10 text-slate-600 mb-3" />
              <p className="text-sm font-semibold text-slate-400">No ingested datasets yet</p>
              <p className="text-[11px] text-slate-500 mt-1 max-w-[300px]">
                Upload a document above to begin real intelligence extraction.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {jobs.map((job) => {
                const status = STATUS_CONFIG[job.status] || STATUS_CONFIG.QUEUED;
                const isExpanded = expandedJobId === job.id;

                return (
                  <div key={job.id} className="border border-slate-800 rounded-xl overflow-hidden">
                    {/* Job row */}
                    <button
                      onClick={() => toggleJobDetail(job.id)}
                      className="w-full p-4 flex items-center justify-between gap-4 hover:bg-slate-950/50 transition-colors text-left"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        {isExpanded ? (
                          <ChevronDown className="h-4 w-4 text-slate-500 shrink-0" />
                        ) : (
                          <ChevronRight className="h-4 w-4 text-slate-500 shrink-0" />
                        )}
                        <FileText className="h-5 w-5 text-slate-400 shrink-0" />
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-slate-200 truncate">{job.file_name}</p>
                          <div className="flex gap-2 mt-0.5 text-[10px] text-slate-500">
                            <span>{job.source_type}</span>
                            <span>•</span>
                            <span>{job.file_type.toUpperCase()}</span>
                            {job.file_size_bytes && (
                              <>
                                <span>•</span>
                                <span>{(job.file_size_bytes / 1024).toFixed(1)} KB</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 shrink-0">
                        {job.entity_count != null && job.status === "COMPLETED" && (
                          <span className="text-[10px] font-bold text-slate-400">
                            {job.entity_count} entities
                          </span>
                        )}
                        <div className={`flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider ${status.color}`}>
                          {status.icon}
                          <span>{status.label}</span>
                        </div>
                      </div>
                    </button>

                    {/* Expanded detail */}
                    {isExpanded && (
                      <div className="border-t border-slate-800 p-4 bg-slate-950/30">
                        {isLoadingDetail ? (
                          <div className="flex items-center justify-center py-6 gap-2 text-slate-500">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-xs">Loading extracted entities...</span>
                          </div>
                        ) : jobDetail && jobDetail.id === job.id ? (
                          <div className="space-y-4">
                            {/* Job metadata */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                              {[
                                { label: "Records", value: jobDetail.record_count ?? "—" },
                                { label: "Entities", value: jobDetail.entity_count ?? "—" },
                                { label: "Status", value: jobDetail.status },
                                { label: "Created", value: new Date(jobDetail.created_at).toLocaleString() },
                              ].map((item) => (
                                <div key={item.label} className="bg-slate-900/60 border border-slate-800 rounded-lg p-2.5">
                                  <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">{item.label}</p>
                                  <p className="text-xs font-semibold text-slate-200 mt-0.5">{String(item.value)}</p>
                                </div>
                              ))}
                            </div>

                            {/* Error message */}
                            {jobDetail.error_message && (
                              <div className="p-3 bg-red-950/20 border border-red-900/30 rounded-lg">
                                <p className="text-[11px] text-red-400">{jobDetail.error_message}</p>
                              </div>
                            )}

                            {/* Entities grouped by type */}
                            {jobDetail.entities.length > 0 ? (
                              <div className="space-y-3">
                                <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Extracted Entity Candidates</h4>
                                {Object.entries(groupEntities(jobDetail.entities)).map(([type, entities]) => {
                                  const config = ENTITY_CONFIG[type] || { icon: <Database className="h-3.5 w-3.5" />, color: "text-slate-400", bg: "bg-slate-500/10 border-slate-500/20" };
                                  return (
                                    <div key={type} className="space-y-1.5">
                                      <div className={`flex items-center gap-1.5 ${config.color}`}>
                                        {config.icon}
                                        <span className="text-[10px] font-bold uppercase tracking-wider">{type}</span>
                                        <span className="text-[9px] text-slate-500 ml-1">({entities.length})</span>
                                      </div>
                                      <div className="flex flex-wrap gap-1.5">
                                        {entities.map((ent) => (
                                          <span
                                            key={ent.id}
                                            className={`inline-flex items-center gap-1 px-2 py-1 rounded-md border text-[11px] font-medium ${config.bg} ${config.color}`}
                                            title={`Method: ${ent.extraction_method}${ent.source_page ? ` | Page: ${ent.source_page}` : ""}${ent.source_row ? ` | Row: ${ent.source_row}` : ""}${ent.confidence != null ? ` | Confidence: ${ent.confidence.toFixed(2)}` : ""}`}
                                          >
                                            {ent.normalized_value || ent.raw_text}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            ) : jobDetail.status === "COMPLETED" ? (
                              <p className="text-xs text-slate-500 text-center py-4">No entities were extracted from this document.</p>
                            ) : null}
                          </div>
                        ) : null}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
