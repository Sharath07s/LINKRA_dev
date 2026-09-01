"use client";

import React, { useState } from "react";
import { ListChecks, Plus } from "lucide-react";

export default function OfficerActionsPanel({ actions, fetchActions }: { actions: any[], fetchActions: () => void }) {
  const [showForm, setShowForm] = useState(false);
  const [actionType, setActionType] = useState("PATROL");
  const [notes, setNotes] = useState("");

  const handleSubmit = async () => {
    if (!notes) return;
    try {
      await fetch("/officer/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action_type: actionType, notes })
      });
      setShowForm(false);
      setNotes("");
      fetchActions();
    } catch (e) {
      console.warn(e);
    }
  };

  return (
    <div suppressHydrationWarning className="h-full bg-slate-900/50 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-slate-800 bg-slate-950/50 flex justify-between items-center">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
          <ListChecks className="h-4 w-4 text-blue-400" /> Action Log
        </h3>
        <button onClick={() => setShowForm(!showForm)} className="bg-blue-600/20 text-blue-400 p-1 rounded hover:bg-blue-600/40">
          <Plus className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {showForm && (
          <div className="bg-slate-900 border border-blue-500/30 p-3 rounded-lg mb-4 space-y-3">
            <select value={actionType} onChange={e => setActionType(e.target.value)} className="w-full bg-slate-950 border border-slate-700 text-xs p-2 rounded text-slate-200">
              <option value="PATROL">ROUTINE PATROL</option>
              <option value="INTERVIEW">FIELD INTERVIEW</option>
              <option value="EVIDENCE_LOG">EVIDENCE COLLECTION</option>
            </select>
            <textarea 
              value={notes} onChange={e => setNotes(e.target.value)}
              placeholder="Enter action notes..." 
              className="w-full bg-slate-950 border border-slate-700 text-xs p-2 rounded text-slate-200 h-20 resize-none"
            />
            <button onClick={handleSubmit} className="w-full bg-blue-600 text-white text-xs font-bold py-2 rounded">LOG ACTION</button>
          </div>
        )}

        {actions.length === 0 ? (
          <div className="text-center text-slate-500 text-xs py-4">No recent actions logged.</div>
        ) : (
          <div className="space-y-3">
            {actions?.map(a => (
              <div key={a.id} className="border-l-2 border-blue-500 pl-3 py-1">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-bold text-slate-300">{a.action_type}</span>
                  <span className="text-[10px] font-mono text-slate-500">{new Date(a.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
                <p className="text-xs text-slate-400">{a.notes}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
