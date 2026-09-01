"use client";

import React from "react";
import { EmptyState } from "@/components/ui/empty-state";
import { Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function TimelineView() {
  return (
    <Card className="bg-card border-border h-[600px] flex flex-col shadow-sm">
      <CardHeader className="pb-3 border-b border-border/50">
        <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
          <Clock className="h-5 w-5 text-amber-500" />
          Chronological Timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 flex items-center justify-center bg-secondary/20">
        <EmptyState
          icon={<Clock className="h-10 w-10 text-muted-foreground" />}
          title="Timeline Intelligence Unavailable"
          description="Chronological events will be displayed here when timeline processing is integrated."
          className="border-none bg-transparent"
        />
      </CardContent>
    </Card>
  );
}
