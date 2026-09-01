"use client";

import React from "react";
import { EmptyState } from "@/components/ui/empty-state";
import { Network } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function GraphContainer() {
  return (
    <Card className="bg-card border-border h-[600px] flex flex-col shadow-sm">
      <CardHeader className="pb-3 border-b border-border/50">
        <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
          <Network className="h-5 w-5 text-primary" />
          Knowledge Graph
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 flex items-center justify-center bg-secondary/20">
        <EmptyState
          icon={<Network className="h-10 w-10 text-muted-foreground" />}
          title="Graph Intelligence Unavailable"
          description="Graph data will appear here when the backend Neo4j graph service is connected. No artificial relationships will be shown."
          className="border-none bg-transparent"
        />
      </CardContent>
    </Card>
  );
}
