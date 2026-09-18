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
    <div suppressHydrationWarning className="h-full bg-[#080808]/50 border border-[#222222] rounded-xl flex flex-col overflow-hidden">
      <div className="p-3 border-b border-[#222222] bg-[#050505]/50 flex justify-between items-center">
        <h3 className="text-xs font-bold text-[#F5F5F5] uppercase tracking-widest flex items-center gap-2">
          <ListChecks className="h-4 w-4 text-[#10B981]" /> Action Log
        </h3>
        <button onClick={() => setShowForm(!showForm)} className="bg-[#10B981]/15 text-[#10B981] p-1 rounded hover:bg-[#10B981]/20">
          <Plus className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {showForm && (
          <div className="bg-[#080808] border border-[#10B981]/30 p-3 rounded-lg mb-4 space-y-3">
            <select value={actionType} onChange={e => setActionType(e.target.value)} className="w-full bg-[#050505] border border-[#2A2A2A] text-xs p-2 rounded text-[#F5F5F5]">
              <option value="PATROL">ROUTINE PATROL</option>
              <option value="INTERVIEW">FIELD INTERVIEW</option>
              <option value="EVIDENCE_LOG">EVIDENCE COLLECTION</option>
            </select>
            <textarea 
              value={notes} onChange={e => setNotes(e.target.value)}
              placeholder="Enter action notes..." 
              className="w-full bg-[#050505] border border-[#2A2A2A] text-xs p-2 rounded text-[#F5F5F5] h-20 resize-none"
            />
            <button onClick={handleSubmit} className="w-full bg-[#10B981] text-white text-xs font-bold py-2 rounded">LOG ACTION</button>
          </div>
        )}

        {actions.length === 0 ? (
          <div className="text-center text-[#666666] text-xs py-4">No recent actions logged.</div>
        ) : (
          <div className="space-y-3">
            {actions?.map(a => (
              <div key={a.id} className="border-l-2 border-[#10B981] pl-3 py-1">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-bold text-[#F5F5F5]">{a.action_type}</span>
                  <span className="text-[10px] font-mono text-[#666666]">{new Date(a.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
                <p className="text-xs text-[#9A9A9A]">{a.notes}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
