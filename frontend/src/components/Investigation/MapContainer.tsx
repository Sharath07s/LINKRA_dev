"use client";

import React from "react";
import { EmptyState } from "@/components/ui/empty-state";
import { Map } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function MapContainer() {
  return (
    <Card className="bg-card border-border h-[600px] flex flex-col shadow-sm">
      <CardHeader className="pb-3 border-b border-border/50">
        <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
          <Map className="h-5 w-5 text-emerald-500" />
          Intelligence Map
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 flex items-center justify-center bg-secondary/20">
        <EmptyState
          icon={<Map className="h-10 w-10 text-muted-foreground" />}
          title="Map Intelligence Unavailable"
          description="Geospatial data and heatmaps will appear here when the backend mapping service is connected."
          className="border-none bg-transparent"
        />
      </CardContent>
    </Card>
  );
}
