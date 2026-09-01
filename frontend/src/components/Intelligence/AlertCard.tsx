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
    LOW: "border-blue-500 text-blue-500 bg-blue-500/10",
    INFO: "border-slate-500 text-slate-400 bg-slate-500/10",
  };

  return (
    <Card className={`bg-slate-900 border-slate-800 border-l-4 ${severityStyles[severity].split(' ')[0]} transition-all hover:bg-slate-800/50`}>
      <CardContent className="p-4 flex flex-col gap-3">
        <div className="flex justify-between items-start">
          <Badge variant="outline" className={`rounded-sm text-[10px] tracking-wider font-bold ${severityStyles[severity]}`}>
            {severity}
          </Badge>
          <span className="text-xs text-slate-500 font-medium">{timestamp}</span>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
          <p className="text-xs text-slate-400 mt-1 line-clamp-2">{reason}</p>
        </div>

        <div className="flex items-center justify-between mt-2 pt-3 border-t border-slate-800/50">
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <Bell className="h-3.5 w-3.5" />
            Source: <span className="text-slate-400 font-medium">{source}</span>
          </div>
          <Button variant="ghost" size="sm" className="h-7 text-xs text-blue-400 hover:text-blue-300 hover:bg-blue-950/30">
            Review
            <ArrowRight className="ml-1 h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
