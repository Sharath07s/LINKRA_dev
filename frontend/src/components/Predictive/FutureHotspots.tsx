"use client";
import { apiClient } from "@/lib/api-client";

import React, { useState, useEffect } from "react";
import { Map, AlertTriangle, Crosshair } from "lucide-react";

export default function FutureHotspots() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/predictive/hotspots")
      .then(r => r.data)
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-full bg-slate-900 border border-slate-800 rounded-xl animate-pulse"></div>;

  const isInsufficient = data?.status === "insufficient_data";

  return (
    <div className="h-full bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800 bg-slate-950/50 flex items-center gap-2">
        <Map className="h-4 w-4 text-amber-500" />
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Emerging Hotspots</h3>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto relative">
        {isInsufficient ? (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-50" />
            <h4 className="text-sm font-bold text-amber-500 mb-1">Insufficient Spatial Data</h4>
            <p className="text-xs text-slate-400 font-mono mb-2">{data.message}</p>
            <div className="inline-flex items-center gap-2 text-[10px] bg-slate-950 px-2 py-1 rounded border border-slate-800">
              <span className="text-slate-500">Available Coords: {data.available_records}</span>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {data?.predicted_hotspots?.map((hs: any, i: number) => (
              <div key={i} className="bg-slate-950 border border-amber-500/20 rounded p-3">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    <Crosshair className="h-3 w-3 text-amber-500" />
                    <span className="text-xs font-bold text-white">Zone {hs.district_id.substring(0, 8)}</span>
                  </div>
                  <span className="text-[10px] font-mono text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                    Escalation: {hs.escalation_rate * 100}%
                  </span>
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                  <span>Lat: {hs.latitude.toFixed(4)}</span>
                  <span>Lon: {hs.longitude.toFixed(4)}</span>
                  <span>Conf: {(hs.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
