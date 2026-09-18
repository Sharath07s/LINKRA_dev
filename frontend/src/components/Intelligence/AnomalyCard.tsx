"use client";

import React from "react";
import { AlertTriangle, Fingerprint, Eye, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface AnomalyCardProps {
  id: string;
  type: string;
  entityName: string;
  reason: string;
  timestamp: string;
  status: "New" | "Investigating" | "Confirmed" | "Dismissed";
}

export function AnomalyCard({ id, type, entityName, reason, timestamp, status }: AnomalyCardProps) {
  const isNew = status === "New";

  return (
    <Card className="bg-[#080808] border-[#222222] hover:border-[#10B981]/20 transition-colors group">
      <CardContent className="p-4 flex flex-col gap-3">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-md ${isNew ? 'bg-amber-950/50 text-amber-500' : 'bg-[#0D0D0D] text-[#9A9A9A]'}`}>
              <AlertTriangle className="h-4 w-4" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-[#F5F5F5]">{type}</h4>
              <p className="text-xs text-[#9A9A9A] font-mono">{id}</p>
            </div>
          </div>
          <Badge variant="outline" className={`
            ${status === 'New' ? 'border-amber-500/50 text-amber-400 bg-amber-950/20' : ''}
            ${status === 'Investigating' ? 'border-[#10B981]/50 text-[#10B981] bg-blue-950/20' : ''}
            ${status === 'Confirmed' ? 'border-red-500/50 text-red-400 bg-red-950/20' : ''}
            ${status === 'Dismissed' ? 'border-slate-500/50 text-[#9A9A9A] bg-[#050505]/20' : ''}
          `}>
            {status}
          </Badge>
        </div>

        <div className="bg-[#050505]/50 rounded p-3 border border-[#222222]/50">
          <div className="flex items-center gap-2 text-sm text-[#F5F5F5] mb-1">
            <Fingerprint className="h-3.5 w-3.5 text-[#666666]" />
            <span className="font-medium text-[#F5F5F5]">{entityName}</span>
          </div>
          <p className="text-xs text-[#9A9A9A] line-clamp-2">{reason}</p>
        </div>

        <div className="flex items-center justify-between mt-1">
          <span className="text-xs text-[#666666]">{timestamp}</span>
          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button variant="ghost" size="sm" className="h-7 text-xs text-[#9A9A9A] hover:text-[#F5F5F5]">
              <Eye className="mr-1 h-3 w-3" />
              View
            </Button>
            <Button variant="ghost" size="sm" className="h-7 text-xs text-[#10B981] hover:text-[#10B981] hover:bg-[#10B981]/10">
              Investigate
              <ArrowRight className="ml-1 h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
