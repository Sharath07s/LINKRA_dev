"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, TrendingUp, Radio } from "lucide-react";

const mockFeeds = [
  { time: "14:22", text: "Vehicle theft cluster detected in Mysuru Central.", icon: AlertTriangle, color: "text-amber-500" },
  { time: "14:16", text: "New criminal network identified linking 3 FIRs.", icon: TrendingUp, color: "text-[#10B981]" },
  { time: "14:09", text: "Repeat offender activity increased in Zone 4.", icon: Radio, color: "text-red-500" },
];

export default function IntelligenceFeedTicker() {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % mockFeeds.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const currentFeed = mockFeeds[currentIndex];
  const Icon = currentFeed.icon;

  return (
    <div className="bg-[#050505] border-b border-[#222222] h-10 w-full flex items-center px-4 overflow-hidden">
      <div className="flex items-center gap-2 mr-4 shrink-0">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
        </span>
        <span className="text-[10px] font-bold text-[#9A9A9A] tracking-widest uppercase">Live Intel</span>
      </div>
      
      <div className="flex-1 flex items-center gap-3 animate-fade-in truncate">
        <span className="text-[10px] text-[#666666] font-mono shrink-0">{currentFeed.time}</span>
        <Icon className={`h-3.5 w-3.5 shrink-0 ${currentFeed.color}`} />
        <span className="text-xs font-medium text-[#F5F5F5] truncate">{currentFeed.text}</span>
      </div>
    </div>
  );
}
