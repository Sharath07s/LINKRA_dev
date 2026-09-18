import { Link2 } from "lucide-react";

export default function SourceAttribution({ sources }: { sources: string[] }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="space-y-2">
      <span className="text-[9px] font-bold text-[#9A9A9A] block uppercase">Evidence Repositories Searched</span>
      <div className="flex flex-wrap gap-2">
        {sources?.map((s, idx) => (
          <div key={idx} className="flex items-center gap-1 bg-[#080808] border border-[#2A2A2A] px-2 py-1 rounded text-[10px] text-[#10B981] hover:bg-[#0D0D0D] cursor-pointer transition-colors">
            <Link2 className="w-3 h-3" />
            <span className="truncate max-w-[150px]">{s}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
