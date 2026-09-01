"use client";
import { apiClient } from "@/lib/api-client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { IntelligenceWorkspace } from "@/components/IntelligenceWorkspace";
import DashboardLayout from "@/components/DashboardLayout";
function KnowledgeGraphContent() {
  const searchParams = useSearchParams();
  const focusId = searchParams.get("focusId");
  const initialFocus = focusId || searchParams.get("focus"); // keep backward compat
  
  return (
    <DashboardLayout>
      <IntelligenceWorkspace initialFocusId={initialFocus} />
    </DashboardLayout>
  );
}

export default function KnowledgeGraphPage() {
  return (
    <Suspense fallback={
      <DashboardLayout>
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-pulse text-cyan-400 text-sm font-semibold">Loading Knowledge Graph…</div>
        </div>
      </DashboardLayout>
    }>
      <KnowledgeGraphContent />
    </Suspense>
  );
}
