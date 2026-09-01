"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/DashboardLayout";
import { useCrimes } from "../../hooks/useCrimes";
import { 
  Search, 
  AlertTriangle, 
  Map, 
  TrendingUp, 
  Activity, 
  FileText, 
  Clock, 
  ArrowRight,
  Shield,
  Filter,
  Eye,
  Plus,
  Sliders,
  ChevronRight,
  AlertCircle
} from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";

export default function DashboardPage() {
  const { data: crimes, isLoading, error } = useCrimes();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCrime, setSelectedCrime] = useState<any>(null);

  // Use live data 
  const crimesList = crimes || [];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    router.push(`/ai-assistant?query=${encodeURIComponent(searchQuery)}`);
  };

  const selectSuggestedPrompt = (prompt: string) => {
    router.push(`/ai-assistant?query=${encodeURIComponent(prompt)}`);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        
        {/* Welcome and Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight sm:text-3xl">LINKRA</h1>
            <p className="text-sm text-muted-foreground">AI-Powered Criminal Intelligence Network</p>
          </div>
          <div className="flex items-center gap-2 rounded-md bg-secondary border border-border p-2 text-xs font-mono text-muted-foreground">
            <Clock className="h-4 w-4 text-primary" />
            <span>SESSION LIFETIME: 07:54:12</span>
          </div>
        </div>

        {/* Global AI Search Panel */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm relative overflow-hidden">
          <form onSubmit={handleSearchSubmit} className="relative flex gap-3 max-w-5xl mx-auto">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-muted-foreground">
                <Search className="h-5 w-5" />
              </div>
              <input
                type="text"
                className="w-full bg-background border border-border hover:border-border/80 focus:border-primary rounded-md pl-11 pr-4 py-3.5 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary transition-all shadow-sm"
                placeholder="Ask LINKRA Copilot for investigation assistance..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button 
              type="submit" 
              className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-md px-6 py-3.5 text-sm font-semibold transition-all shadow flex items-center gap-2"
            >
              <span>Query Copilot</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </form>
        </div>

        {/* Four Core Stat Widgets */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Stat 1 */}
          <div className="p-5 bg-card border border-border rounded-xl flex flex-col justify-between relative group hover:border-border/80 transition-all duration-200 shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-muted-foreground text-xs font-semibold uppercase tracking-wider">Active Investigations</p>
                <h3 className="text-2xl font-bold mt-1 text-foreground">{isLoading ? "—" : crimesList.length}</h3>
              </div>
              <div className="p-2.5 bg-primary/10 rounded-md border border-primary/20 text-primary">
                <Activity className="h-5 w-5" />
              </div>
            </div>
          </div>

          {/* Stat 2 */}
          <div className="p-5 bg-card border border-border rounded-xl flex flex-col justify-between relative group hover:border-border/80 transition-all duration-200 shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-muted-foreground text-xs font-semibold uppercase tracking-wider">Critical Alerts</p>
                <h3 className="text-2xl font-bold mt-1 text-foreground">—</h3>
              </div>
              <div className="p-2.5 bg-destructive/10 rounded-md border border-destructive/20 text-destructive">
                <AlertTriangle className="h-5 w-5" />
              </div>
            </div>
          </div>

          {/* Stat 3 */}
          <div className="p-5 bg-card border border-border rounded-xl flex flex-col justify-between relative group hover:border-border/80 transition-all duration-200 shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-muted-foreground text-xs font-semibold uppercase tracking-wider">AI Predictive Forecasts</p>
                <h3 className="text-2xl font-bold mt-1 text-foreground">—</h3>
              </div>
              <div className="p-2.5 bg-indigo-500/10 rounded-md border border-indigo-500/20 text-indigo-400">
                <Shield className="h-5 w-5" />
              </div>
            </div>
          </div>

          {/* Stat 4 */}
          <div className="p-5 bg-card border border-border rounded-xl flex flex-col justify-between relative group hover:border-border/80 transition-all duration-200 shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-muted-foreground text-xs font-semibold uppercase tracking-wider">Pending Reports</p>
                <h3 className="text-2xl font-bold mt-1 text-foreground">—</h3>
              </div>
              <div className="p-2.5 bg-amber-500/10 rounded-md border border-amber-500/20 text-amber-500">
                <FileText className="h-5 w-5" />
              </div>
            </div>
          </div>

        </div>

        {/* Middle Section: Alerts Feed & District Hotspots Map Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Critical Alerts Feed */}
          <div className="lg:col-span-5 bg-card border border-border rounded-xl flex flex-col h-[400px] overflow-hidden shadow-sm">
            <div className="flex items-center justify-between border-b border-border p-4 bg-secondary/30">
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-foreground text-sm tracking-tight">Security & Modus Operandi Alerts</h3>
              </div>
            </div>

            <div className="flex-1 p-4">
              <EmptyState 
                title="No Active Alerts" 
                description="There are currently no critical security alerts in your jurisdiction."
                icon={<AlertCircle className="h-8 w-8 text-muted-foreground" />} 
              />
            </div>
          </div>

          {/* Crime Map Preview Card */}
          <div className="lg:col-span-7 bg-card border border-border rounded-xl flex flex-col h-[400px] relative overflow-hidden shadow-sm">
            <div className="flex justify-between items-center border-b border-border p-4 bg-secondary/30 z-10">
              <div>
                <h3 className="font-bold text-foreground text-sm tracking-tight">Strategic Threat & Hotspot Forecast</h3>
              </div>
              <button 
                onClick={() => router.push("/crime-map")}
                className="flex items-center gap-1 px-3 py-1.5 bg-background hover:bg-secondary border border-border rounded-md text-xs text-foreground transition-colors font-semibold"
              >
                <span>Full Screen Analysis</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>

            <div className="flex-1 p-4">
              <EmptyState 
                title="Geospatial Service Inactive" 
                description="Live map telemetry requires an active connection to the geospatial subsystem."
                icon={<Map className="h-8 w-8 text-muted-foreground" />} 
              />
            </div>
          </div>

        </div>

        {/* Bottom Section: Latest FIRs Table */}
        <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-border p-4 bg-secondary/30">
            <div>
              <h3 className="font-bold text-foreground text-base tracking-tight">Active First Information Reports (FIRs)</h3>
              <p className="text-xs text-muted-foreground mt-0.5">Real-time case log synchronizing CCTNS databases</p>
            </div>
            <div className="flex gap-2">
              <button className="flex items-center gap-1.5 px-3 py-1.5 bg-background border border-border hover:bg-secondary text-muted-foreground hover:text-foreground rounded-md text-xs font-semibold transition-colors shadow-sm">
                <Filter className="h-3.5 w-3.5" />
                <span>Filter Districts</span>
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 bg-background border border-border hover:bg-secondary text-muted-foreground hover:text-foreground rounded-md text-xs font-semibold transition-colors shadow-sm">
                <Sliders className="h-3.5 w-3.5" />
                <span>Customize Columns</span>
              </button>
            </div>
          </div>

          <div className="p-4">
            {isLoading ? (
              <LoadingState message="Loading investigations..." />
            ) : error ? (
              <ErrorState title="Failed to load investigations" description="An error occurred while fetching FIR data from the backend." />
            ) : crimesList.length === 0 ? (
              <EmptyState title="No Investigations Found" description="There are no active investigations in the database." />
            ) : (
              <div className="overflow-x-auto w-full border border-border rounded-md">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-border text-[10px] font-bold text-muted-foreground uppercase tracking-widest bg-secondary/50">
                      <th className="py-3 px-4">FIR Number</th>
                      <th className="py-3 px-4">Crime Classification</th>
                      <th className="py-3 px-4">District Sector</th>
                      <th className="py-3 px-4">Police Jurisdiction</th>
                      <th className="py-3 px-4">Registration Date</th>
                      <th className="py-3 px-4 text-center">Threat Rating</th>
                      <th className="py-3 px-4 text-center">Case Status</th>
                      <th className="py-3 px-4 text-right">Intel Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border text-xs">
                    {crimesList?.map((crime: any) => (
                      <tr key={crime.id} className="hover:bg-secondary/30 transition-colors group">
                        <td className="py-3.5 px-4 font-mono font-bold text-primary group-hover:text-primary/80">
                          {crime.fir_number}
                        </td>
                        <td className="py-3.5 px-4 font-semibold text-foreground">
                          {crime.title}
                        </td>
                        <td className="py-3.5 px-4 text-muted-foreground">
                          {crime.district}
                        </td>
                        <td className="py-3.5 px-4 text-muted-foreground">
                          {crime.station}
                        </td>
                        <td className="py-3.5 px-4 font-mono text-muted-foreground">
                          {crime.date}
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <span className={`inline-block px-2 py-0.5 rounded-sm text-[10px] font-bold uppercase ${
                            crime.severity === "High" 
                              ? "bg-destructive/10 text-destructive border border-destructive/20" 
                              : crime.severity === "Medium"
                              ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                              : "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                          }`}>
                            {crime.severity}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-center">
                          <span className={`inline-flex items-center gap-1.5 text-[10px] font-semibold ${
                            crime.status === "Under Investigation" 
                              ? "text-primary" 
                              : crime.status === "FIR Registered"
                              ? "text-amber-500"
                              : "text-muted-foreground"
                          }`}>
                            <span className={`h-1.5 w-1.5 rounded-full ${
                              crime.status === "Under Investigation" 
                                ? "bg-primary animate-pulse" 
                                : crime.status === "FIR Registered"
                                ? "bg-amber-500"
                                : "bg-muted-foreground"
                            }`} />
                            {crime.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <button 
                            onClick={() => setSelectedCrime(crime)}
                            className="p-1 px-2.5 bg-background hover:bg-secondary border border-border rounded-md text-[10px] font-bold text-muted-foreground hover:text-foreground transition-all flex items-center gap-1 ml-auto shadow-sm"
                          >
                            <Eye className="h-3 w-3" />
                            <span>Inspect</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Case Inspector side drawer */}
      {selectedCrime && (
        <div className="fixed inset-0 z-50 flex justify-end bg-background/60 backdrop-blur-sm">
          <div className="w-full max-w-xl bg-card border-l border-border p-6 md:p-8 flex flex-col h-full shadow-2xl animate-in slide-in-from-right duration-250">
            {/* Header */}
            <div className="flex justify-between items-start border-b border-border pb-4">
              <div>
                <span className="font-mono text-xs text-primary font-bold">{selectedCrime.fir_number}</span>
                <h2 className="text-xl font-bold text-foreground mt-1 leading-snug">{selectedCrime.title}</h2>
              </div>
              <button 
                onClick={() => setSelectedCrime(null)}
                className="p-1.5 bg-secondary border border-border hover:bg-secondary/80 text-muted-foreground rounded-md transition-colors"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>

            {/* Content body */}
            <div className="flex-1 overflow-y-auto py-6 space-y-6 pr-2">
              
              {/* Core Attributes Grid */}
              <div className="grid grid-cols-2 gap-4 bg-background border border-border rounded-xl p-4 shadow-sm">
                <div>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase block">Crime Type</span>
                  <span className="text-xs font-semibold text-foreground">{selectedCrime.type}</span>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase block">Threat Index</span>
                  <span className={`inline-block px-2 py-0.5 rounded-sm text-[10px] font-bold uppercase mt-0.5 ${
                    selectedCrime.severity === "High" 
                      ? "bg-destructive/10 text-destructive border border-destructive/20" 
                      : selectedCrime.severity === "Medium"
                      ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                      : "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                  }`}>
                    {selectedCrime.severity}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase block">Police Station</span>
                  <span className="text-xs text-foreground">{selectedCrime.station} ({selectedCrime.district})</span>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase block">Registration Date</span>
                  <span className="text-xs font-mono text-foreground">{selectedCrime.date}</span>
                </div>
              </div>

              {/* Modus Operandi */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Modus Operandi (M.O.)</h4>
                <div className="p-4 bg-secondary/30 rounded-xl border border-border leading-relaxed text-xs text-foreground shadow-sm">
                  {selectedCrime.modus_operandi}
                </div>
              </div>

              {/* Suspects linked */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Associated Suspect Profiles</h4>
                <div className="space-y-2">
                  {selectedCrime.suspects?.map((suspect: string, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-background rounded-xl border border-border shadow-sm">
                      <span className="text-xs font-semibold text-foreground">{suspect}</span>
                      <button 
                        onClick={() => {
                          setSelectedCrime(null);
                          router.push(`/knowledge-graph?focus=${encodeURIComponent(suspect)}`);
                        }}
                        className="text-[10px] font-bold text-primary hover:text-primary/80 underline"
                      >
                        Inspect Node Link
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Security Audit Badge */}
              <div className="p-4 bg-background border border-border rounded-xl space-y-2 shadow-sm">
                <div className="flex items-center gap-2 text-destructive font-bold text-[10px] uppercase">
                  <Shield className="h-4 w-4" />
                  <span>Audit Trail & Classification</span>
                </div>
                <p className="text-[10px] text-muted-foreground leading-normal">
                  Access to FIR file records has been registered under active user session logs. This information is classified as law enforcement sensitive and must not be copied or distributed outside police firewalls.
                </p>
              </div>

            </div>

            {/* Footer buttons */}
            <div className="border-t border-border pt-4 flex gap-3">
              <button 
                onClick={() => {
                  setSelectedCrime(null);
                  router.push(`/ai-assistant?query=Analyze%20links%20for%2520${encodeURIComponent(selectedCrime.fir_number)}`);
                }}
                className="flex-1 py-2.5 bg-primary hover:bg-primary/90 text-primary-foreground rounded-md text-xs font-bold text-center transition-colors shadow"
              >
                Analyze Case with AI
              </button>
              <button 
                onClick={() => setSelectedCrime(null)}
                className="px-4 py-2.5 bg-secondary border border-border hover:bg-secondary/80 text-foreground rounded-md text-xs font-bold transition-colors shadow-sm"
              >
                Close Drawer
              </button>
            </div>
          </div>
        </div>
      )}

    </DashboardLayout>
  );
}
