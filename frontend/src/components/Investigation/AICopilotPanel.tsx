"use client";

import React from "react";
import { EmptyState } from "@/components/ui/empty-state";
import { MessageSquare } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function AICopilotPanel() {
  return (
    <Card className="bg-card border-border h-[600px] flex flex-col shadow-sm">
      <CardHeader className="pb-3 border-b border-border/50">
        <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
          <MessageSquare className="h-5 w-5 text-indigo-500" />
          AI Copilot
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 flex items-center justify-center bg-secondary/20">
        <EmptyState
          icon={<MessageSquare className="h-10 w-10 text-muted-foreground" />}
          title="AI Assistant Not Connected"
          description="Evidence-grounded AI interactions will take place here when the intelligence engine is connected."
          className="border-none bg-transparent"
        />
      </CardContent>
    </Card>
  );
}
