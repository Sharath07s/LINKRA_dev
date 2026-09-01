"use client";
import { apiClient } from "@/lib/api-client";

import { useState, useEffect } from "react";
import { Search, Loader2 } from "lucide-react";

export default function GlobalSearchBar() {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<{ id: string; type: string; title: string; subtitle: string }[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    const searchTimer = setTimeout(async () => {
      setIsSearching(true);
      setShowDropdown(true);
      try {
        // Integrate with /api/v1/search when available. For now simulate federation:
        // const res = await apiClient.get(`/api/v1/search?q=${query}`);
        // const data = res.data;
        
        // Remove fake data per SIH requirement, return empty results until backend is integrated
        setResults([]);
      } catch (err) {
        console.warn(err);
      } finally {
        setIsSearching(false);
      }
    }, 500);

    return () => clearTimeout(searchTimer);
  }, [query]);

  return (
    <div className="relative flex-1 max-w-2xl mx-4">
      <div className="relative flex items-center w-full">
        <div className="absolute left-3 text-slate-400">
          <Search className="h-4 w-4" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Global Search (Entities, FIRs, Vehicles, Phones)..."
          className="w-full bg-slate-900 border border-slate-700 text-slate-100 text-sm rounded-lg pl-10 pr-10 py-2 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all placeholder-slate-500"
        />
        <div className="absolute right-3 text-slate-400">
          {isSearching && <Loader2 className="h-4 w-4 animate-spin" />}
        </div>
      </div>
      
      {showDropdown && (
        <div className="absolute mt-2 w-full bg-slate-900 border border-slate-700 rounded-lg shadow-xl shadow-black/50 z-50 overflow-hidden">
          {results.length > 0 ? (
            <ul>
              {results?.map((r, i) => (
                <li key={i} className="px-4 py-3 hover:bg-slate-800 border-b border-slate-800/50 cursor-pointer flex flex-col transition-colors">
                  <span className="text-sm font-semibold text-blue-400">{r.title}</span>
                  <span className="text-xs text-slate-400">{r.type.toUpperCase()} • {r.subtitle}</span>
                </li>
              ))}
            </ul>
          ) : !isSearching ? (
            <div className="px-4 py-6 text-center text-sm text-slate-500">
              No results found for "{query}".
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
