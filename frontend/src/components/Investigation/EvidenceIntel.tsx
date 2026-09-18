import React from "react";
import { HardDrive, Smartphone, FileArchive, ArrowUpRight } from "lucide-react";

export default function EvidenceIntel({ investigationId }: { investigationId?: string }) {
  const evidenceItems: any[] = [];

  return (
    <div className="bg-[#080808]/40 border border-[#222222] rounded-2xl flex flex-col h-full">
      <div className="p-4 border-b border-[#222222]">
        <h3 className="text-sm font-bold text-white tracking-wide">Evidence Intelligence</h3>
      </div>
      <div className="p-4 flex-1 flex items-center justify-center">
        {evidenceItems.length > 0 ? (
          <div className="w-full h-full overflow-y-auto space-y-3">
            {evidenceItems.map((item, idx) => {
              const Icon = item.icon || HardDrive;
              return (
                <div key={idx} className="bg-[#050505]/50 border border-slate-850 p-3 rounded-xl flex items-center justify-between group hover:border-[#2A2A2A] transition-colors cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-[#080808] border border-[#222222] flex items-center justify-center text-[#9A9A9A]">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-[#F5F5F5]">{item.name}</span>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[9px] text-[#666666] font-mono">{item.id}</span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#0D0D0D] text-[#F5F5F5] font-semibold">{item.status}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[10px] font-bold text-[#10B981] flex items-center gap-1">
                      {item.linkedNodes} Links
                      <ArrowUpRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center">
             <div className="w-12 h-12 mx-auto rounded-full bg-[#0D0D0D]/50 flex items-center justify-center border border-[#2A2A2A]/50 mb-4">
               <FileArchive className="h-5 w-5 text-[#666666]" />
             </div>
             <h4 className="text-sm font-semibold text-[#F5F5F5] mb-1">No Evidence</h4>
             <p className="text-xs text-[#666666] max-w-[200px] mx-auto">
               No physical or digital evidence has been cataloged for this case.
             </p>
          </div>
        )}
      </div>
    </div>
  );
}
