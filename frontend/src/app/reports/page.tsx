"use client";

import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { 
  FileText, 
  Download, 
  Plus, 
  CheckCircle, 
  FileCheck, 
  ShieldCheck, 
  Sliders, 
  Clock, 
  Play, 
  AlertCircle,
  FileSpreadsheet,
  BookOpen
} from "lucide-react";

interface IntelligenceReport {
  id: string;
  title: string;
  type: string;
  scope: string;
  createdDate: string;
  status: "Verified & Signed" | "Pending Review" | "Draft";
  size: string;
  hash: string;
}

const INITIAL_REPORTS: IntelligenceReport[] = [
  { id: "r1", title: "Burglary MO Spatiotemporal Assessment - Mysuru", type: "Hotspot Analysis", scope: "District-wide", createdDate: "2026-06-05", status: "Verified & Signed", size: "1.8 MB", hash: "SHA256: 4b29f...9c4a" },
  { id: "r2", title: "ATM Jackpotting Cyber-Physical Briefing", type: "Case Brief", scope: "Case-specific", createdDate: "2026-06-06", status: "Verified & Signed", size: "2.1 MB", hash: "SHA256: 8d10e...fa7b" },
  { id: "r3", title: "Vicky Saluja Smuggling Ties & Phone Log Graph", type: "Network Analysis", scope: "Suspect-centric", createdDate: "2026-06-04", status: "Pending Review", size: "4.2 MB", hash: "SHA256: 1a99c...dd34" },
  { id: "r4", title: "Cyber Blackmail Trend Summary - Karnataka Region", type: "Trend Report", scope: "Regional", createdDate: "2026-06-01", status: "Verified & Signed", size: "3.5 MB", hash: "SHA256: 7f12b...bb88" }
];

export default function ReportsPage() {
  const [reports, setReports] = useState<IntelligenceReport[]>(INITIAL_REPORTS);
  
  // Form controls
  const [title, setTitle] = useState("");
  const [type, setType] = useState("Case Brief");
  const [scope, setScope] = useState("Case-specific");

  // Compilation state
  const [compilingStep, setCompilingStep] = useState(0); // 0: Idle, 1-4: Compiling steps, 5: Finished
  const [compilingLog, setCompilingLog] = useState("");
  const [newlyGeneratedReport, setNewlyGeneratedReport] = useState<IntelligenceReport | null>(null);

  const startCompilation = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setNewlyGeneratedReport(null);
    setCompilingStep(1);
    setCompilingLog("Initiating secure connection handshake...");

    setTimeout(() => {
      setCompilingStep(2);
      setCompilingLog("Querying CCTNS crime registries & local databases...");
    }, 1000);

    setTimeout(() => {
      setCompilingStep(3);
      setCompilingLog("Traversing Neo4j suspect relationship nodes...");
    }, 2000);

    setTimeout(() => {
      setCompilingStep(4);
      setCompilingLog("Synthesizing generative LLM brief & spatiotemporal map plots...");
    }, 3000);

    setTimeout(() => {
      setCompilingStep(5);
      setCompilingLog("Affixing digital watermark & cryptographic SHA-256 signature...");
    }, 4000);

    setTimeout(() => {
      const reportId = "rep-" + Date.now();
      const generatedHash = "SHA256: " + Math.random().toString(16).substring(2, 8) + "..." + Math.random().toString(16).substring(2, 6);
      
      const newReport: IntelligenceReport = {
        id: reportId,
        title: title,
        type: type,
        scope: scope,
        createdDate: new Date().toISOString().substring(0, 10),
        status: "Verified & Signed",
        size: (Math.random() * 3 + 1.2).toFixed(1) + " MB",
        hash: generatedHash
      };

      setReports([newReport, ...reports]);
      setNewlyGeneratedReport(newReport);
      setCompilingStep(6);
      setCompilingLog("Official brief compiled successfully!");
      setTitle("");
    }, 5200);
  };

  const handleDownload = (report: IntelligenceReport) => {
    // Simulate downloading PDF by showing a simple alert or log entry
    alert(`Initiating download for encrypted file:\n[${report.title}.pdf]\nSecurity Hash: ${report.hash}\nAccess logged for audit tracking.`);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">Intelligence Reporting Center</h1>
            <p className="text-sm text-slate-400">Generate verified, cryptographically signed crime intelligence summaries and case briefs</p>
          </div>
          <div className="flex items-center gap-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 px-3 py-1 text-[10px] font-bold text-blue-400 uppercase">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <span>FIPS 140-2 COMPLIANT</span>
          </div>
        </div>

        {/* Top Split: Create Report & Compilation Console */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Create Report Form */}
          <div className="lg:col-span-5 bg-slate-900/40 border border-slate-800 p-5 rounded-2xl">
            <h3 className="font-bold text-white text-base border-b border-slate-800 pb-3 mb-4">
              Formulate Intelligence Report
            </h3>
            
            <form onSubmit={startCompilation} className="space-y-4">
              {/* Title */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Report Subject / Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Vicky Saluja Interstate Auto-smuggling Brief"
                  className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  value={title}
                  disabled={compilingStep > 0 && compilingStep < 6}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              {/* Type Select */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Report Template</label>
                <select
                  className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none"
                  value={type}
                  disabled={compilingStep > 0 && compilingStep < 6}
                  onChange={(e) => setType(e.target.value)}
                >
                  <option>Case Brief</option>
                  <option>Hotspot Analysis</option>
                  <option>Network Analysis</option>
                  <option>Trend Report</option>
                </select>
              </div>

              {/* Scope Select */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Investigation Scope</label>
                <select
                  className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none"
                  value={scope}
                  disabled={compilingStep > 0 && compilingStep < 6}
                  onChange={(e) => setScope(e.target.value)}
                >
                  <option>Case-specific</option>
                  <option>Suspect-centric</option>
                  <option>Regional</option>
                  <option>National</option>
                </select>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={compilingStep > 0 && compilingStep < 6}
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-blue-500/15 flex items-center justify-center gap-1.5"
              >
                <Play className="h-3.5 w-3.5" />
                <span>Compile Official Brief</span>
              </button>

            </form>
          </div>

          {/* Compile Progress Console */}
          <div className="lg:col-span-7 bg-slate-950/40 border border-slate-800 p-5 rounded-2xl flex flex-col min-h-[268px]">
            <h3 className="font-bold text-white text-sm uppercase tracking-wider border-b border-slate-850 pb-3 mb-4">
              Cryptographic Compiler Output
            </h3>

            {compilingStep === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 space-y-2">
                <BookOpen className="h-8 w-8 text-slate-650" />
                <p className="text-xs font-semibold">Compiler Idle</p>
                <p className="text-[10px] text-slate-600 max-w-[200px]">Configure parameters on the left to start compiling official files</p>
              </div>
            ) : (
              <div className="flex-1 flex flex-col justify-between space-y-4">
                
                {/* Steps logs */}
                <div className="space-y-2.5 font-mono text-[11px]">
                  <div className="flex items-center gap-2 text-slate-400">
                    <span className="text-blue-400 font-bold">&#8250;</span>
                    <span>{compilingLog}</span>
                  </div>
                  
                  {/* Progress indicator bars */}
                  <div className="grid grid-cols-5 gap-1.5 pt-2">
                    {[1, 2, 3, 4, 5]?.map((s) => (
                      <div 
                        key={s} 
                        className={`h-2.5 rounded transition-all ${
                          compilingStep >= s 
                            ? "bg-gradient-to-r from-blue-500 to-indigo-500 shadow-md shadow-blue-500/20" 
                            : "bg-slate-900 border border-slate-850"
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {/* Newly Generated Details */}
                {compilingStep === 6 && newlyGeneratedReport && (
                  <div className="p-4 bg-emerald-950/5 border border-emerald-900/35 rounded-xl space-y-3 animate-in fade-in duration-200">
                    <div className="flex items-center gap-2 text-emerald-400 font-bold text-[10px] uppercase">
                      <FileCheck className="h-4.5 w-4.5" />
                      <span>Report Compilation Complete</span>
                    </div>

                    <div className="text-xs space-y-1.5 text-slate-350">
                      <p><span className="font-semibold text-slate-200">Title:</span> {newlyGeneratedReport.title}</p>
                      <p><span className="font-semibold text-slate-200">Secure Hash:</span> <span className="font-mono text-slate-300">{newlyGeneratedReport.hash}</span></p>
                    </div>

                    <div className="flex gap-2">
                      <button 
                        onClick={() => handleDownload(newlyGeneratedReport)}
                        className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-[10px] font-bold transition-all flex items-center gap-1 shadow-md shadow-emerald-600/10"
                      >
                        <Download className="h-3 w-3" />
                        <span>Download Encrypted PDF</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Audit Warning */}
                <div className="p-3 bg-slate-950 border border-slate-850 rounded-xl flex items-start gap-2 text-[9px] text-slate-500">
                  <AlertCircle className="h-4 w-4 text-slate-550 shrink-0 mt-0.5" />
                  <p className="leading-relaxed">
                    Compiling documents registers an entry in the national audit log detailing badge code, system parameters, and active IP. Exported PDFs contain digital classification watermarks.
                  </p>
                </div>

              </div>
            )}
          </div>

        </div>

        {/* Existing generated reports list */}
        <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl">
          <div className="flex justify-between items-center border-b border-slate-800/80 pb-4 mb-4">
            <div>
              <h3 className="font-bold text-white text-lg">Generated Intelligence Briefings</h3>
              <p className="text-xs text-slate-400">Archived PDF files signed with platform key credentials</p>
            </div>
            <button className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-950 border border-slate-800 hover:bg-slate-900 text-slate-400 hover:text-slate-200 rounded-lg text-xs font-semibold transition-colors">
              <Sliders className="h-3.5 w-3.5" />
              <span>Manage Archives</span>
            </button>
          </div>

          {/* List display */}
          <div className="space-y-3">
            {reports?.map((report) => (
              <div 
                key={report.id} 
                className="p-4 bg-slate-950/40 hover:bg-slate-950/70 border border-slate-850 hover:border-slate-750/80 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="h-10 w-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 shrink-0">
                    <FileText className="h-5.5 w-5.5" />
                  </div>
                  <div className="min-w-0">
                    <h4 className="font-bold text-slate-250 text-xs md:text-sm truncate">{report.title}</h4>
                    <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1 text-[10px] text-slate-500 font-medium">
                      <span>TYPE: <span className="text-slate-400 font-semibold">{report.type}</span></span>
                      <span>•</span>
                      <span>SCOPE: <span className="text-slate-400 font-semibold">{report.scope}</span></span>
                      <span>•</span>
                      <span>DATE: <span className="text-slate-400 font-mono">{report.createdDate}</span></span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between md:justify-end gap-6 shrink-0">
                  <div className="flex flex-col items-end text-right">
                    <span className={`inline-block px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                      report.status === "Verified & Signed" 
                        ? "bg-emerald-500/10 text-emerald-450 border border-emerald-500/20" 
                        : "bg-amber-500/10 text-amber-450 border border-amber-500/20"
                    }`}>
                      {report.status}
                    </span>
                    <span className="text-[9px] font-mono text-slate-550 mt-1">{report.hash}</span>
                  </div>

                  <div className="flex gap-2">
                    <button 
                      onClick={() => handleDownload(report)}
                      className="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-350 hover:text-slate-100 rounded-lg transition-all"
                      title="Download PDF"
                    >
                      <Download className="h-4.5 w-4.5" />
                    </button>
                  </div>
                </div>

              </div>
            ))}
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
