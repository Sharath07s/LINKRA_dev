"use client";

import React from "react";
import { Bell, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface AlertCardProps {
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
  title: string;
  reason: string;
  timestamp: string;
  source: string;
}

export function AlertCard({ severity, title, reason, timestamp, source }: AlertCardProps) {
  const severityStyles = {
    CRITICAL: "border-red-500 text-red-500 bg-red-500/10",
    HIGH: "border-amber-500 text-amber-500 bg-amber-500/10",
    MEDIUM: "border-yellow-500 text-yellow-500 bg-yellow-500/10",
    LOW: "border-[#10B981] text-[#10B981] bg-[#10B981]/10",
    INFO: "border-slate-500 text-[#9A9A9A] bg-slate-500/10",
  };

  return (
    <Card className={`bg-[#080808] border-[#222222] border-l-4 ${severityStyles[severity].split(' ')[0]} transition-all hover:bg-[#0D0D0D]/50`}>
      <CardContent className="p-4 flex flex-col gap-3">
        <div className="flex justify-between items-start">
          <Badge variant="outline" className={`rounded-sm text-[10px] tracking-wider font-bold ${severityStyles[severity]}`}>
            {severity}
          </Badge>
          <span className="text-xs text-[#666666] font-medium">{timestamp}</span>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-[#F5F5F5]">{title}</h4>
          <p className="text-xs text-[#9A9A9A] mt-1 line-clamp-2">{reason}</p>
        </div>

        <div className="flex items-center justify-between mt-2 pt-3 border-t border-[#222222]/50">
          <div className="flex items-center gap-1.5 text-xs text-[#666666]">
            <Bell className="h-3.5 w-3.5" />
            Source: <span className="text-[#9A9A9A] font-medium">{source}</span>
          </div>
          <Button variant="ghost" size="sm" className="h-7 text-xs text-[#10B981] hover:text-[#10B981] hover:bg-[#10B981]/10">
            Review
            <ArrowRight className="ml-1 h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
