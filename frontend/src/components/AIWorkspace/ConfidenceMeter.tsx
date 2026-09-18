export default function ConfidenceMeter({ confidence }: { confidence: number }) {
  let colorClass = "from-emerald-500 to-teal-400";
  let textColor = "text-emerald-400";
  
  if (confidence < 70) {
    colorClass = "from-amber-500 to-yellow-400";
    textColor = "text-amber-400";
  }
  if (confidence < 40) {
    colorClass = "from-red-500 to-orange-400";
    textColor = "text-red-400";
  }

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[9px] font-bold text-[#9A9A9A]">
        <span>AI CONFIDENCE COEFFICIENT</span>
        <span className={textColor}>{confidence}%</span>
      </div>
      <div className="h-1.5 w-full bg-[#080808] rounded-full overflow-hidden">
        <div 
          className={`h-full bg-gradient-to-r ${colorClass} rounded-full`} 
          style={{ width: `${confidence}%` }}
        />
      </div>
    </div>
  );
}
