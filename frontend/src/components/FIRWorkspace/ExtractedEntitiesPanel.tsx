"use client";
import { apiClient } from "@/lib/api-client";

import React, { useEffect, useState } from "react";
import { Users, Car, Smartphone, MapPin, Building, Package } from "lucide-react";

interface EntitiesProps {
  firId: string;
}

export default function ExtractedEntitiesPanel({ firId }: EntitiesProps) {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const res = await apiClient.get(`/crimes/${firId}/entities`);
        if (res.status === 200) {
          const json = res.data;
          setData(json);
        }
      } catch (err) {
        console.warn("Failed to fetch entities:", err);
      } finally {
        setIsLoading(false);
      }
    };
    if (firId) fetchEntities();
  }, [firId]);

  if (isLoading) return <div className="h-full bg-slate-900/40 border border-slate-800 rounded-2xl animate-pulse"></div>;
  if (!data) return null;

  const entityGroups = [
    { title: "Suspects", icon: Users, items: data.suspects, key1: "name", key2: "role", color: "text-red-400" },
    { title: "Vehicles", icon: Car, items: data.vehicles, key1: "registration", key2: "type", color: "text-amber-400" },
    { title: "Phones", icon: Smartphone, items: data.phones, key1: "number", key2: "provider", color: "text-blue-400" },
    { title: "Locations", icon: MapPin, items: data.locations, key1: "address", key2: "type", color: "text-emerald-400" },
    { title: "Organizations", icon: Building, items: data.organizations, key1: "name", key2: "type", color: "text-purple-400" },
    { title: "Evidence", icon: Package, items: data.evidence, key1: "name", key2: "type", color: "text-slate-400" },
  ];

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-slate-800 bg-slate-950/50">
        <h3 className="text-sm font-bold text-white tracking-wide">Extracted Entities</h3>
      </div>
      <div className="p-4 flex-1 overflow-y-auto space-y-4">
        {entityGroups?.map((group, idx) => {
          if (!group.items || group.items.length === 0) return null;
          const Icon = group.icon;
          return (
            <div key={idx} className="space-y-2">
              <span className={`text-[10px] font-bold uppercase tracking-widest flex items-center gap-1.5 ${group.color}`}>
                <Icon className="h-3 w-3" /> {group.title}
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {group.items?.map((item: any, i: number) => (
                  <div key={i} className="bg-slate-950/60 border border-slate-800 p-2.5 rounded-lg flex flex-col group hover:border-slate-700 transition-colors cursor-pointer">
                    <span className="text-xs font-bold text-slate-200">{item[group.key1]}</span>
                    <span className="text-[10px] text-slate-500">{item[group.key2]}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
