"use client";

import DashboardLayout from "@/components/DashboardLayout";
import { EmptyState } from "@/components/ui/empty-state";
import { FolderOpen } from "lucide-react";

export default function EvidencePage() {
  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Evidence Repository</h1>
            <p className="text-muted-foreground mt-1">Global view of all ingested and verified evidence.</p>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl">
          <EmptyState 
            icon={<FolderOpen className="h-10 w-10 text-muted-foreground" />}
            title="No Evidence Available" 
            description="Upload or connect data sources to ingest evidence. Verified items will appear here." 
          />
        </div>
      </div>
    </DashboardLayout>
  );
}
