"use client";
import React, { useEffect, useState } from 'react';
import { useRealtime } from '@/components/Providers/RealtimeProvider';

export default function EventNotificationCenter() {
  const { lastEvent } = useRealtime();
  const [toast, setToast] = useState<{ id: string; message: string; type: string } | null>(null);

  useEffect(() => {
    if (!lastEvent) return;

    let message = "";
    let type = "info";

    switch (lastEvent.event_type) {
      case "CRIME_CREATED":
        message = `New FIR Registered: ${lastEvent.payload?.fir_number || 'Unknown'}`;
        type = "warning";
        break;
      case "ALERT_CREATED":
        message = `New Alert [${lastEvent.payload?.severity}]: ${lastEvent.payload?.title}`;
        type = "error";
        break;
      case "PREDICTION_UPDATED":
        message = `Predictive Intelligence Model Refreshed.`;
        type = "success";
        break;
      case "MODEL_DRIFT_DETECTED":
        message = `Warning: Prediction Drift Detected.`;
        type = "error";
        break;
      case "ALERT_RESOLVED":
        message = `Alert Resolved: ${lastEvent.payload?.alert_id}`;
        type = "success";
        break;
      default:
        return; // Don't toast everything
    }

    const id = Math.random().toString(36).substr(2, 9);
    setToast({ id, message, type });

    const timer = setTimeout(() => {
      setToast(prev => prev?.id === id ? null : prev);
    }, 5000);

    return () => clearTimeout(timer);
  }, [lastEvent]);

  if (!toast) return null;

  const bgColors = {
    info: 'bg-[#10B981] border-blue-400',
    warning: 'bg-amber-600 border-amber-400',
    error: 'bg-red-600 border-red-400',
    success: 'bg-emerald-600 border-emerald-400'
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-slide-up">
      <div className={`px-6 py-4 rounded-lg shadow-2xl border flex items-center gap-3 text-white ${bgColors[toast.type as keyof typeof bgColors]}`}>
        {toast.type === 'error' && <span className="text-xl">⚠️</span>}
        {toast.type === 'warning' && <span className="text-xl">⚡</span>}
        {toast.type === 'success' && <span className="text-xl">✓</span>}
        {toast.type === 'info' && <span className="text-xl">ℹ️</span>}
        <p className="font-medium">{toast.message}</p>
      </div>
    </div>
  );
}
