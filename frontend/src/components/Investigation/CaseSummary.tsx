"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, FileText, AlertTriangle, ShieldCheck } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";

export function CaseSummary({ crime }: { crime?: any }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <div className="lg:col-span-2 flex flex-col gap-6">
        <Card className="bg-card border-border shadow-sm">
          <CardHeader className="pb-3 border-b border-border/50">
            <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
              <FileText className="h-5 w-5 text-primary" />
              Investigation Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <p className="text-muted-foreground leading-relaxed">
              {crime?.modus_operandi ? crime.modus_operandi : "No detailed summary or modus operandi is available for this case yet."}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border shadow-sm">
          <CardHeader className="pb-3 border-b border-border/50">
            <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
              <Users className="h-5 w-5 text-amber-500" />
              Key Entities
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {crime?.suspects && crime.suspects.length > 0 ? (
              <div className="divide-y divide-border">
                {crime.suspects.map((suspect: string, i: number) => (
                  <div key={i} className="p-4 flex items-center justify-between hover:bg-secondary/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-full bg-secondary flex items-center justify-center text-muted-foreground">
                        <Users className="h-5 w-5" />
                      </div>
                      <div>
                        <h4 className="font-medium text-foreground">{suspect}</h4>
                        <p className="text-xs text-muted-foreground">Known Suspect</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8">
                <EmptyState 
                  title="No Entities Identified" 
                  description="There are currently no known suspects or entities linked to this investigation." 
                />
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col gap-6">
        <Card className="bg-card border-border shadow-sm">
          <CardHeader className="pb-3 border-b border-border/50">
            <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              Priority Intelligence
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 flex flex-col gap-4">
            <EmptyState 
              title="No Priority Alerts" 
              description="No automated alerts or priority intelligence detected for this case." 
              className="border-none py-10"
            />
          </CardContent>
        </Card>
      </div>

    </div>
  );
}
