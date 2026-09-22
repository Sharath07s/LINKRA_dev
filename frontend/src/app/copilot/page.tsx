"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import DashboardLayout from "@/components/DashboardLayout";
import { useAuthStore } from "../../store/authStore";
import { 
  Send, 
  Bot, 
  User, 
  Mic, 
  MicOff, 
  Trash2, 
  Sparkles, 
  ChevronDown, 
  ShieldAlert, 
  BarChart3, 
  MapPin, 
  Link2, 
  ChevronRight, 
  HelpCircle,
  FolderPlus,
  FileDown,
  Info,
  Layers
} from "lucide-react";
import ConfidenceMeter from "@/components/AIWorkspace/ConfidenceMeter";
import SourceAttribution from "@/components/AIWorkspace/SourceAttribution";
import ReasoningTracePanel from "@/components/AIWorkspace/ReasoningTracePanel";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  kannadaContent?: string;
  intent?: string;
  structuredData?: Record<string, any>[];
  recordCount?: number;
  intelData?: {
    type: "chart" | "map" | "network";
    title: string;
    chartValues?: { label: string; value: number }[];
    mapDetails?: { area: string; risk: "High" | "Medium"; count: number }[];
    networkLinks?: { from: string; relation: string; to: string }[];
  };
  xaiDetails?: {
    confidence: number;
    sources: string[];
    reasoning: string[];
  };
}

const HISTORIC_CONVERSATIONS = [
  { id: "h1", title: "Burglary MO overlap Mysuru", date: "Today" },
  { id: "h2", title: "ATM Jackpotting suspects BLR", date: "Yesterday" },
  { id: "h3", title: "Cyber blackmail cluster MNG", date: "3 days ago" },
  { id: "h4", title: "Suspect phone log tower logs", date: "1 week ago" }
];

const SUGGESTED_PROMPTS = [
  { text: "Analyze burglary patterns in Mysuru", icon: MapPin },
  { text: "Find repeat offender links for Vicky Saluja", icon: Link2 },
  { text: "Compare ATM jackpotting trends across districts", icon: BarChart3 }
];

// ── Lightweight Markdown → HTML renderer (no deps) ─────────────
function renderMarkdown(md: string): string {
  let html = md
    // Escape HTML entities
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Tables: detect lines with pipes
  const lines = html.split('\n');
  let inTable = false;
  const processed: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const isTableRow = line.startsWith('|') && line.endsWith('|');
    const isSeparator = /^\|[\s\-:|]+\|$/.test(line);

    if (isTableRow && !inTable) {
      inTable = true;
      processed.push('<table>');
      // Header row
      const cells = line.split('|')?.filter(c => c.trim() !== '');
      processed.push('<thead><tr>' + cells?.map(c => `<th>${c.trim()}</th>`).join('') + '</tr></thead>');
      // Skip separator row
      if (i + 1 < lines.length && /^\|[\s\-:|]+\|$/.test(lines[i + 1].trim())) {
        i++;
      }
      processed.push('<tbody>');
    } else if (isTableRow && inTable && !isSeparator) {
      const cells = line.split('|')?.filter(c => c.trim() !== '');
      processed.push('<tr>' + cells?.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>');
    } else if (isSeparator) {
      // skip
    } else {
      if (inTable) {
        processed.push('</tbody></table>');
        inTable = false;
      }
      processed.push(line);
    }
  }
  if (inTable) processed.push('</tbody></table>');

  html = processed.join('\n');

  // Bold: **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic: *text*
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Inline code: `text`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Unordered list items: - text
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>[\s\S]*?<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`);
  // Paragraphs (blank-line separated blocks)
  html = html.replace(/\n{2,}/g, '</p><p>');
  html = `<p>${html}</p>`;
  // Clean up empty paragraphs
  html = html.replace(/<p>\s*<\/p>/g, '');
  // Line breaks within paragraphs
  html = html.replace(/\n/g, '<br/>');

  return html;
}

function AIAssistantPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { token } = useAuthStore();
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [language, setLanguage] = useState<"EN" | "KA">("EN");
  const [isRecording, setIsRecording] = useState(false);
  const [expandedXaiId, setExpandedXaiId] = useState<string | null>(null);

  // Check URL params for queries passed from Dashboard
  useEffect(() => {
    const urlQuery = searchParams.get("query");
    if (urlQuery && messages.length === 0) {
      executeSearch(decodeURIComponent(urlQuery));
    }
  }, [searchParams]);

  // Scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const executeSearch = async (queryText: string) => {
    if (!queryText.trim()) return;
    
    // Add user message
    const userMsgId = "msg-" + Date.now();
    const newUserMessage: Message = {
      id: userMsgId,
      role: "user",
      content: queryText,
      kannadaContent: translateToKannada(queryText)
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setInput("");
    setIsTyping(true);
    setErrorState(null);

    try {
      // Import chatService dynamically to avoid SSR issues if any, or just use it if imported
      const { chatService } = await import('@/services/chat.service');
      const response = await chatService.sendMessage(queryText);
      
      const aiResponse: Message = {
        id: "ai-" + Date.now(),
        role: "assistant",
        content: response.answer,
        intent: response.intent,
        structuredData: response.evidence ?? undefined,
        recordCount: response.evidence ? response.evidence.length : 0,
        xaiDetails: {
           confidence: response.grounded ? 100 : (response.provider === "system_fallback" ? 95 : 85),
           sources: response.evidence?.length > 0 ? response.evidence.map((s: any) => `${s.type}: ${s.title}`) : [`Provider: ${response.provider || 'unknown'}`, `Intent: ${response.intent || 'general'}`],
           reasoning: [
             `Status: ${response.status}`,
             `Entities Found: ${response.entities ? response.entities.length : 0}`,
             `Analytics Generated: ${response.analytics ? response.analytics.length : 0}`,
           ].concat(response.warnings || [])
        }
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setExpandedXaiId(aiResponse.id);
    } catch (error: any) {
      console.warn("Chat error:", error);
      setErrorState(error.message || "Failed to communicate with the assistant.");
      
      const errorResponse: Message = {
        id: "err-" + Date.now(),
        role: "assistant",
        content: `Error: ${error.message || "Failed to connect to the backend AI service."}`
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    executeSearch(input);
  };

  const simulateVoiceRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      // Simulate recognized text
      setInput("Show burglary hotspots in Mysuru");
    } else {
      setIsRecording(true);
      setErrorState(null);
    }
  };

  const [errorState, setErrorState] = useState<string | null>(null);

  const clearChat = () => {
    setMessages([]);
    setExpandedXaiId(null);
  };

  // Very simple helper to translate basic English phrases to Kannada for datathon MVP fidelity
  const translateToKannada = (enText: string) => {
    const text = enText.toLowerCase();
    if (text.includes("burglary") || text.includes("mysuru")) {
      return "ಮೈಸೂರಿನಲ್ಲಿ ಕನ್ನಗಳ್ಳತನದ ಹಾಟ್‌ಸ್ಪಾಟ್‌ಗಳನ್ನು ತೋರಿಸಿ";
    }
    if (text.includes("vicky") || text.includes("offender")) {
      return "ವಿಕ್ಕಿ ಸಲೂಜಾ ಶಂಕಿತ ಲಿಂಕ್‌ಗಳನ್ನು ಪತ್ತೆ ಮಾಡಿ";
    }
    if (text.includes("atm") || text.includes("jackpotting")) {
      return "ಎಟಿಎಂ ದರೋಡೆ ಪ್ರಕರಣಗಳ ವಿಶ್ಲೇಷಣೆ";
    }
    return `ಅಪರಾಧ ದಾಖಲೆಗಳ ಪ್ರಶ್ನೆ: "${enText}"`;
  };

  return (
    <DashboardLayout>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-8.5rem)] min-h-[500px]">
        
        {/* Left Side Pane: History & Templates */}
        <div className="hidden lg:flex lg:col-span-3 flex-col bg-[#080808]/40 border border-[#222222] rounded-2xl p-4 overflow-hidden h-full">
          <div className="flex justify-between items-center pb-3 border-b border-[#222222]">
            <span className="text-xs font-bold text-[#F5F5F5] uppercase tracking-wider">Intel Sessions</span>
            <button 
              onClick={clearChat}
              className="text-[#666666] hover:text-red-400 p-1 rounded-lg transition-colors"
              title="Clear Active Session"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>

          {/* Quick Prompts List */}
          <div className="mt-4 space-y-2">
            <span className="text-[10px] font-bold text-[#666666] uppercase tracking-wider block">Templates</span>
            {SUGGESTED_PROMPTS?.map((prompt, idx) => {
              const Icon = prompt.icon;
              return (
                <button
                  key={idx}
                  onClick={() => executeSearch(prompt.text)}
                  className="flex items-center gap-2.5 w-full text-left p-2.5 bg-[#050505]/40 border border-slate-850 hover:border-[#2A2A2A]/80 rounded-xl text-xs text-[#9A9A9A] hover:text-[#F5F5F5] transition-all group"
                >
                  <Icon className="h-4 w-4 text-[#10B981] shrink-0 group-hover:scale-105 transition-transform" />
                  <span className="truncate leading-snug">{prompt.text}</span>
                </button>
              );
            })}
          </div>

          {/* History log */}
          <div className="flex-1 overflow-y-auto mt-6 space-y-2 pr-1">
            <span className="text-[10px] font-bold text-[#666666] uppercase tracking-wider block">History Logs</span>
            {HISTORIC_CONVERSATIONS?.map((hist) => (
              <div
                key={hist.id}
                onClick={() => executeSearch(hist.title)}
                className="flex items-center justify-between p-2.5 rounded-xl border border-transparent hover:border-[#222222] hover:bg-[#050505]/20 cursor-pointer transition-all text-xs"
              >
                <div className="flex flex-col min-w-0">
                  <span className="text-[#F5F5F5] font-medium truncate">{hist.title}</span>
                  <span className="text-[9px] text-[#666666] mt-0.5">{hist.date}</span>
                </div>
                <ChevronRight className="h-3.5 w-3.5 text-[#666666] shrink-0" />
              </div>
            ))}
          </div>

          {/* Assistant status badge */}
          <div className="border-t border-slate-850 pt-3.5 mt-auto flex items-center gap-2">
            <div className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </div>
            <span className="text-[10px] font-semibold text-[#9A9A9A]">LINKRA NLP CORE V2.4 ACTIVE</span>
          </div>
        </div>

        {/* Right Side Pane: Chat Dialog */}
        <div className="lg:col-span-9 flex flex-col bg-[#080808]/40 border border-[#222222] rounded-2xl overflow-hidden h-full">
          
          {/* Active Header */}
          <div className="p-4 border-b border-[#222222] bg-[#061224]/80 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/10">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-white text-sm">Conversational Intelligence Assistant</h3>
                <p className="text-[10px] text-[#9A9A9A]">Secure RAG & Explainable AI analysis engine</p>
              </div>
            </div>

            {/* Language Selector */}
            <div className="flex items-center bg-[#050505] border border-slate-850 p-0.5 rounded-lg text-xs font-semibold">
              <button 
                onClick={() => setLanguage("EN")}
                className={`px-2 py-1 rounded-md transition-all ${
                  language === "EN" ? "bg-[#10B981] text-white" : "text-[#9A9A9A] hover:text-[#F5F5F5]"
                }`}
              >
                ENGLISH
              </button>
              <button 
                onClick={() => setLanguage("KA")}
                className={`px-2 py-1 rounded-md transition-all ${
                  language === "KA" ? "bg-[#10B981] text-white" : "text-[#9A9A9A] hover:text-[#F5F5F5]"
                }`}
              >
                ಕನ್ನಡ
              </button>
            </div>
          </div>

          {/* Messages Viewport */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto space-y-4">
                <div className="h-12 w-12 rounded-full bg-[#10B981]/10 border border-[#10B981]/20 flex items-center justify-center text-[#10B981]">
                  <Sparkles className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="font-bold text-white text-sm">Initiate Analytical Query</h4>
                  <p className="text-xs text-[#9A9A9A] mt-1">
                    Ask about specific suspects, crime trends, or spatial clusters in Karnataka. The assistant matches data patterns from CCTNS and SCRB databases.
                  </p>
                </div>
                <div className="w-full grid grid-cols-1 gap-2 pt-2">
                  {SUGGESTED_PROMPTS?.map((p, idx) => (
                    <button
                      key={idx}
                      onClick={() => executeSearch(p.text)}
                      className="px-4 py-2.5 bg-[#050505] border border-slate-850 hover:border-[#2A2A2A]/80 rounded-xl text-xs text-[#9A9A9A] hover:text-[#F5F5F5] transition-all font-medium text-left"
                    >
                      {p.text}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages?.map((msg) => {
                  const isUser = msg.role === "user";
                  return (
                    <div key={msg.id} className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
                      {/* Avatar */}
                      {!isUser && (
                        <div className="h-8 w-8 rounded-lg bg-blue-950 border border-blue-900 text-[#10B981] flex items-center justify-center shrink-0">
                          <Bot className="h-4.5 w-4.5" />
                        </div>
                      )}
                      
                      <div className="space-y-3 max-w-[85%]">
                        {/* Bubble */}
                        <div className={`p-4 rounded-2xl leading-relaxed text-xs border ${
                          isUser 
                            ? "bg-gradient-to-r from-blue-600/25 to-indigo-600/15 border-[#10B981]/30 text-[#F5F5F5] rounded-tr-none" 
                            : "bg-[#050505]/60 border-slate-850 text-[#F5F5F5] rounded-tl-none"
                        }`}>
                          <div className="prose prose-sm prose-invert max-w-none [&_table]:w-full [&_table]:text-[10px] [&_th]:bg-[#080808] [&_th]:px-2 [&_th]:py-1.5 [&_th]:text-left [&_th]:font-bold [&_th]:text-[#F5F5F5] [&_th]:border [&_th]:border-[#222222] [&_td]:px-2 [&_td]:py-1.5 [&_td]:border [&_td]:border-[#222222]/60 [&_td]:text-[#F5F5F5] [&_code]:text-[#10B981] [&_code]:bg-[#080808]/80 [&_code]:px-1 [&_code]:rounded [&_strong]:text-white [&_ul]:space-y-1 [&_li]:text-[#F5F5F5] [&_p]:text-[#F5F5F5] [&_em]:text-[#9A9A9A]" dangerouslySetInnerHTML={{ __html: renderMarkdown(language === "EN" ? msg.content : (msg.kannadaContent || msg.content)) }} />
                        </div>

                        {/* Rich Intel Data Component (If exists) */}
                        {!isUser && msg.intelData && (
                          <div className="bg-[#050505]/40 border border-slate-850 rounded-xl p-4 space-y-3">
                            <span className="text-[10px] font-bold text-[#9A9A9A] uppercase block tracking-wider">
                              Visual Component: {msg.intelData.title}
                            </span>
                            
                            {/* SVG Chart representation */}
                            {msg.intelData.type === "chart" && msg.intelData.chartValues && (
                              <div className="space-y-2.5">
                                {msg.intelData.chartValues?.map((cv, idx) => (
                                  <div key={idx} className="space-y-1">
                                    <div className="flex justify-between text-[10px] font-semibold text-[#F5F5F5]">
                                      <span>{cv.label}</span>
                                      <span>{cv.value}%</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-[#080808] rounded-full overflow-hidden">
                                      <div 
                                        className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full" 
                                        style={{ width: `${cv.value}%` }}
                                      />
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Spatiotemporal Map component */}
                            {msg.intelData.type === "map" && msg.intelData.mapDetails && (
                              <div className="space-y-2">
                                {msg.intelData.mapDetails?.map((md, idx) => (
                                  <div key={idx} className="flex justify-between items-center p-2 bg-[#080808]/60 rounded-lg border border-slate-850">
                                    <div className="flex items-center gap-2">
                                      <MapPin className="h-3.5 w-3.5 text-red-400" />
                                      <span className="text-xs font-medium text-[#F5F5F5]">{md.area}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                      <span className="text-[10px] text-[#9A9A9A] font-semibold">{md.count} Incidents</span>
                                      <span className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase ${
                                        md.risk === "High" ? "bg-red-500/10 text-red-400" : "bg-amber-500/10 text-amber-400"
                                      }`}>
                                        {md.risk} Risk
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Graph snippet component */}
                            {msg.intelData.type === "network" && msg.intelData.networkLinks && (
                              <div className="space-y-2">
                                {msg.intelData.networkLinks?.map((nl, idx) => (
                                  <div key={idx} className="flex items-center gap-2 text-[10px] bg-[#080808]/60 p-2 rounded-lg border border-slate-850 text-[#F5F5F5]">
                                    <span className="font-semibold text-[#10B981]">{nl.from}</span>
                                    <span className="text-[9px] text-[#666666] font-mono uppercase bg-[#050505] px-2 py-0.5 rounded border border-[#222222]">
                                      {nl.relation}
                                    </span>
                                    <span className="font-semibold text-amber-500">{nl.to}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Explainable AI (XAI) Panel */}
                        {!isUser && msg.xaiDetails && (
                          <div className="border border-slate-850 rounded-xl overflow-hidden">
                            <button
                              onClick={() => setExpandedXaiId(expandedXaiId === msg.id ? null : msg.id)}
                              className="w-full flex items-center justify-between px-4 py-2 bg-[#050505] hover:bg-[#080808] transition-colors text-[10px] font-bold tracking-wider text-[#9A9A9A] uppercase"
                            >
                              <span className="flex items-center gap-1.5">
                                <Info className="h-3.5 w-3.5 text-[#10B981]" />
                                <span>Explainable AI (XAI) Verification</span>
                              </span>
                              <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${
                                expandedXaiId === msg.id ? "rotate-180" : ""
                              }`} />
                            </button>
                            
                            {expandedXaiId === msg.id && (
                              <div className="p-4 bg-[#050505]/30 border-t border-slate-850 space-y-4">
                                <ConfidenceMeter confidence={msg.xaiDetails.confidence} />
                                <SourceAttribution sources={msg.xaiDetails.sources} />
                                <ReasoningTracePanel reasoning={msg.xaiDetails.reasoning} />
                              </div>
                            )}
                          </div>
                        )}

                        {/* Message actions */}
                        {!isUser && (
                          <div className="flex gap-2">
                            <button className="flex items-center gap-1 px-2.5 py-1 bg-[#050505] hover:bg-[#080808] border border-slate-850 rounded text-[10px] font-bold text-[#9A9A9A] hover:text-[#F5F5F5] transition-colors">
                              <FolderPlus className="h-3 w-3" />
                              <span>Pin to Intel Board</span>
                            </button>
                            <button 
                              onClick={() => router.push("/reports")}
                              className="flex items-center gap-1 px-2.5 py-1 bg-[#050505] hover:bg-[#080808] border border-slate-850 rounded text-[10px] font-bold text-[#9A9A9A] hover:text-[#F5F5F5] transition-colors"
                            >
                              <FileDown className="h-3 w-3" />
                              <span>Export PDF Brief</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            {isTyping && (
              <div className="flex gap-3 justify-start">
                <div className="h-8 w-8 rounded-lg bg-blue-950 border border-blue-900 text-[#10B981] flex items-center justify-center shrink-0">
                  <Bot className="h-4.5 w-4.5 animate-pulse" />
                </div>
                <div className="bg-[#050505]/60 border border-slate-850 px-4 py-3.5 rounded-2xl rounded-tl-none flex gap-1.5 items-center">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-100"></span>
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-200"></span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Form Input Footer */}
          <div className="p-4 bg-[#061224]/80 border-t border-[#222222]/80">
            <form onSubmit={handleSendSubmit} className="flex gap-3 max-w-5xl mx-auto relative items-center">
              
              {/* Mic Icon */}
              <button
                type="button"
                onClick={simulateVoiceRecording}
                className={`p-3 rounded-xl border transition-all ${
                  isRecording 
                    ? "bg-red-500/20 border-red-500 text-red-500 animate-pulse" 
                    : "bg-[#050505] border-slate-850 text-[#9A9A9A] hover:text-[#F5F5F5] hover:border-[#2A2A2A]"
                }`}
                title="Simulate Voice Input"
              >
                {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>

              <div className="relative flex-1">
                <input
                  type="text"
                  className="w-full bg-[#050505] border border-slate-850 hover:border-[#222222] rounded-xl px-4 py-3 text-xs text-[#F5F5F5] placeholder-slate-550 focus:outline-none focus:ring-2 focus:ring-[#10B981]/30 transition-all pr-10"
                  placeholder={
                    isRecording 
                      ? "Listening to voice input... Click mic icon to submit"
                      : language === "EN" 
                      ? "Ask about crime connections, district hotspots, or suspects..." 
                      : "ಮೈಸೂರಿನಲ್ಲಿ ಕನ್ನಗಳ್ಳತನದ ಹಾಟ್‌ಸ್ಪಾಟ್‌ಗಳನ್ನು ತೋರಿಸಿ..."
                  }
                  value={input}
                  disabled={isRecording}
                  onChange={(e) => setInput(e.target.value)}
                />
              </div>

              <button 
                type="submit" 
                disabled={!input.trim() || isTyping}
                className="bg-[#10B981] hover:bg-blue-500 disabled:opacity-40 p-3 rounded-xl text-white transition-all shadow-md shadow-blue-600/10"
              >
                <Send className="h-5 w-5" />
              </button>
            </form>

            {/* Voice Waveform animation simulation */}
            {isRecording && (
              <div className="flex justify-center items-center gap-1 mt-3">
                <span className="w-1 h-3 bg-red-500 animate-pulse"></span>
                <span className="w-1 h-5 bg-red-500 animate-pulse delay-75"></span>
                <span className="w-1 h-8 bg-red-500 animate-pulse delay-150"></span>
                <span className="w-1 h-4 bg-red-500 animate-pulse delay-75"></span>
                <span className="w-1 h-2 bg-red-500 animate-pulse"></span>
                <span className="text-[10px] text-red-500 font-mono font-bold tracking-widest ml-2">SIMULATING VOICE CAPTURE</span>
              </div>
            )}
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}

export default function AIAssistantPage() {
  return (
    <Suspense fallback={
      <div className="flex h-screen w-screen items-center justify-center bg-[#030914] text-white">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[#10B981] border-t-transparent"></div>
          <p className="text-sm font-medium text-[#9A9A9A]">Loading AI Assistant...</p>
        </div>
      </div>
    }>
      <AIAssistantPageContent />
    </Suspense>
  );
}
