"use client";

import React, { useState } from "react";
import { BrainCircuit, Send, Search } from "lucide-react";
import { apiClient } from "@/lib/api-client";

export default function OfficerCopilot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: "user", content: input };
    setMessages([...messages, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await apiClient.post("/officer/copilot", { query: userMsg.content });
      if (res.status === 200) {
        const data = res.data;
        setMessages(prev => [...prev, { role: "assistant", ...data }]);
      }
    } catch (err) {
      console.warn(err);
      setMessages(prev => [...prev, { role: "assistant", response: "System error contacting Copilot uplink." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[600px] bg-card border border-border rounded-xl flex flex-col overflow-hidden shadow-sm">
      <div className="p-4 border-b border-border bg-secondary/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg border border-primary/20">
            <BrainCircuit className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground tracking-tight">AI Officer Copilot</h3>
            <p className="text-[10px] text-emerald-500 font-mono tracking-widest uppercase">Secured & Grounded</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center opacity-50">
            <BrainCircuit className="h-10 w-10 text-primary mb-3" />
            <p className="text-sm font-bold text-muted-foreground">"What should I investigate next?"</p>
          </div>
        )}
        
        {messages?.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-xl p-3 ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary/50 border border-border text-foreground'}`}>
              {msg.role === 'user' ? (
                <p className="text-sm">{msg.content}</p>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm leading-relaxed">{msg.response}</p>
                  
                  {msg.priority_actions && msg.priority_actions.length > 0 && (
                    <div className="bg-background p-3 rounded border border-border shadow-sm">
                      <span className="text-[10px] font-bold text-amber-500 uppercase tracking-widest block mb-1">Priority Actions</span>
                      <ul className="text-xs text-muted-foreground list-disc pl-4 space-y-1">
                        {msg.priority_actions?.map((act: string, j: number) => <li key={j}>{act}</li>)}
                      </ul>
                    </div>
                  )}
                  
                  {msg.evidence_used && msg.evidence_used.length > 0 && (
                    <div className="flex gap-2 flex-wrap mt-2">
                      {msg.evidence_used?.map((ev: string, j: number) => (
                        <span key={j} className="text-[9px] font-mono bg-background text-muted-foreground px-1.5 py-0.5 rounded border border-border">
                          SOURCE: {ev}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-secondary/50 rounded-xl p-3 border border-border">
              <span className="text-sm text-muted-foreground flex items-center gap-2">
                <Search className="h-4 w-4 animate-spin text-primary" /> Querying Databases...
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="p-3 border-t border-border bg-secondary/30">
        <div className="relative">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Copilot for tactical advice..."
            className="w-full bg-background border border-border rounded-lg pl-4 pr-12 py-3 text-sm text-foreground focus:outline-none focus:border-primary transition-colors shadow-sm"
          />
          <button 
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="absolute right-2 top-2 bottom-2 aspect-square bg-primary hover:bg-primary/90 disabled:bg-secondary rounded flex items-center justify-center transition-colors shadow-sm"
          >
            <Send className="h-4 w-4 text-primary-foreground" />
          </button>
        </div>
      </div>
    </div>
  );
}
