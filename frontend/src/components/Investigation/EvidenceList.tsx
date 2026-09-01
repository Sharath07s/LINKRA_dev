"use client";

import React from "react";
import { EmptyState } from "@/components/ui/empty-state";
import { FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function EvidenceList() {
  return (
    <Card className="bg-card border-border h-[600px] flex flex-col shadow-sm">
      <CardHeader className="pb-3 border-b border-border/50">
        <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
          <FileText className="h-5 w-5 text-muted-foreground" />
          Evidence & Provenance
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 flex items-center justify-center bg-secondary/20">
        <EmptyState
          icon={<FileText className="h-10 w-10 text-muted-foreground" />}
          title="No Evidence Available"
          description="Evidence records and provenance chains will appear here once connected."
          className="border-none bg-transparent"
        />
      </CardContent>
    </Card>
  );
}
