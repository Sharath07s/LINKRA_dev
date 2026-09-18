import React from "react";
import { Sparkles, FileSearch, Users, Car, Network, PlusCircle } from "lucide-react";
import ConfidenceMeter from "../AIWorkspace/ConfidenceMeter";
import ReasoningTracePanel from "../AIWorkspace/ReasoningTracePanel";

export default function AICopilot() {
  const suggestions = [
    { label: "Find potential suspects", icon: Users },
    { label: "Search related FIRs", icon: FileSearch },
    { label: "Identify connected vehicles", icon: Car },
    { label: "Map criminal network", icon: Network },
  ];

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/10 border-b border-[#222222] p-4 flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-purple-400" />
        <h3 className="text-sm font-bold text-white tracking-wide">AI Investigation Copilot</h3>
      </div>
      
      <div className="p-5 flex-1 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-full bg-[#0D0D0D]/50 flex items-center justify-center border border-[#2A2A2A]/50 mb-4">
          <Sparkles className="h-5 w-5 text-purple-400/50" />
        </div>
        <h4 className="text-sm font-semibold text-[#F5F5F5] mb-1">Copilot Ready</h4>
        <p className="text-xs text-[#666666] max-w-[250px]">
          The AI Copilot is standing by. Ask a question or run an analysis to generate insights for this investigation.
        </p>
      </div>
      
      <div className="p-4 border-t border-[#222222]/50 bg-[#050505]/30">
        <div className="flex items-center gap-2 bg-[#080808] border border-[#222222] rounded-lg p-2 px-3">
          <input 
            type="text" 
            placeholder="Ask Copilot to analyze this case..." 
            className="bg-transparent border-none outline-none text-xs text-[#F5F5F5] flex-1 placeholder:text-[#666666]"
            disabled
          />
          <button className="text-purple-400 opacity-50 cursor-not-allowed">
            <Sparkles className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
