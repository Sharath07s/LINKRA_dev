"use client";
import { useState, useRef, useEffect } from "react";
import { Send, Bot, AlertTriangle, FileText, Search, ShieldAlert } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import ReactMarkdown from "react-markdown";

interface CopilotMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: string;
  sources?: any[];
  evidence?: any[];
  provider?: string;
  warnings?: string[];
  status?: string;
}

export function CopilotPanel({ investigationId, entityId }: { investigationId?: string, entityId?: string }) {
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg: CopilotMessage = { id: Date.now().toString(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await apiClient.post("/copilot/chat", {
        message: userMsg.content,
        investigation_id: investigationId || null,
        entity_id: entityId || null
      });
      
      const assistantMsg: CopilotMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.data.answer,
        intent: res.data.intent,
        evidence: res.data.evidence,
        provider: res.data.provider,
        warnings: res.data.warnings || [],
        status: res.data.status
      };
      
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: CopilotMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Failed to communicate with AI Copilot. The backend service may be unavailable.",
        status: "ERROR"
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-slate-800 bg-slate-950 flex items-center gap-2">
        <Bot className="h-4 w-4 text-blue-400" />
        <span className="font-bold text-xs uppercase text-slate-300 tracking-wider">AI Copilot</span>
        {entityId && <span className="ml-auto text-[9px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">Context: Entity</span>}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2 opacity-60">
            <Search className="h-8 w-8 mb-2" />
            <p className="text-xs font-semibold">Ask about the investigation...</p>
            <p className="text-[10px] text-center max-w-[200px]">"Why was this entity flagged?"<br/>"What evidence supports this link?"</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div className={`max-w-[85%] rounded-xl p-3 text-xs ${
                msg.role === "user" 
                  ? "bg-blue-600/20 border border-blue-500/30 text-blue-100" 
                  : "bg-slate-950 border border-slate-800 text-slate-300"
              }`}>
                {msg.role === "assistant" ? (
                  <div className="prose prose-invert prose-xs max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>
              
              {/* Evidence citations */}
              {msg.role === "assistant" && msg.evidence && msg.evidence.length > 0 && (
                <div className="mt-1.5 max-w-[85%] flex flex-wrap gap-1">
                  {msg.evidence.slice(0, 3).map((ev: any, idx: number) => (
                    <div key={idx} className="flex items-center gap-1 bg-emerald-950/40 border border-emerald-900/50 rounded px-1.5 py-0.5 text-[8px] text-emerald-400">
                      <FileText className="h-2.5 w-2.5" />
                      <span className="truncate max-w-[100px]">{ev.title}</span>
                    </div>
                  ))}
                  {msg.evidence.length > 3 && (
                    <span className="text-[8px] text-slate-500 flex items-center px-1">+{msg.evidence.length - 3} more</span>
                  )}
                </div>
              )}
              
              {/* Disclaimer */}
              {msg.role === "assistant" && msg.status !== "PROVIDER_UNAVAILABLE" && msg.status !== "INSUFFICIENT_DATA" && msg.status !== "ERROR" && (
                <div className="mt-1 flex items-center gap-1 text-[8px] text-slate-500 italic max-w-[85%]">
                  <ShieldAlert className="h-2.5 w-2.5" />
                  <span>Responses reflect structural graph and extracted evidence, not confirmed criminality.</span>
                </div>
              )}
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex items-start">
            <div className="bg-slate-950 border border-slate-800 text-slate-500 rounded-xl p-3 text-xs flex items-center gap-2">
              <span className="animate-pulse">Analyzing intelligence...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-3 bg-slate-950 border-t border-slate-800">
        <div className="relative flex items-center">
          <input
            type="text"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-3 pr-10 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="Ask AI Copilot..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={loading}
          />
          <button 
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="absolute right-2 p-1.5 text-blue-500 hover:text-blue-400 disabled:opacity-50 disabled:hover:text-blue-500"
          >
            <Send className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  );
}
