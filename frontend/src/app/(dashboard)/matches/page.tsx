"use client";

import { useEffect, useState } from "react";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import EmptyState from "@/components/ui/EmptyState";
import MatchCard from "@/components/matches/MatchCard";
import api from "@/lib/api";
import type { Match, MatchStatus } from "@/lib/types";

const FILTERS: { value: MatchStatus | "all"; label: string }[] = [
  { value: "all", label: "Todos" },
  { value: "pending_company_decision", label: "Tu decisión" },
  { value: "pending_worker", label: "Esperando trabajador" },
  { value: "accepted", label: "Aceptados" },
  { value: "rejected_worker", label: "Declinados" },
];

export default function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    async function load() {
      try {
        const params = filter !== "all" ? `?status=${filter}` : "";
        const res = await api.get(`/api/matches${params}`);
        setMatches(res.data);
      } catch { /* handled */ }
      finally { setLoading(false); }
    }
    load();
  }, [filter]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Matches</h1>

      <div className="flex gap-2 flex-wrap">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => { setFilter(f.value); setLoading(true); }}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === f.value
                ? "bg-amber-100 text-amber-700"
                : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : matches.length > 0 ? (
        <div className="space-y-3">
          {matches.map((m) => <MatchCard key={m.id} match={m} />)}
        </div>
      ) : (
        <EmptyState title="No hay matches" description="No hay matches que mostrar con este filtro." />
      )}
    </div>
  );
}
