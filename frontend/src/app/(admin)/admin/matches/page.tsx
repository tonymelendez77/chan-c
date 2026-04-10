"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import { fetchMatches } from "@/lib/admin-api";
import { TRADE_LABELS } from "@/lib/types";
import type { Match } from "@/lib/types";

const STATUS_FILTERS = [
  { value: "", label: "Todos" },
  { value: "pending_company_decision", label: "Esp. decisión" },
  { value: "pending_worker", label: "Esp. trabajador" },
  { value: "call_in_progress", label: "IA activa" },
  { value: "accepted", label: "Aceptados" },
];

export default function AdminMatchesPage() {
  const router = useRouter();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchMatches(filter ? `status=${filter}` : "").then(setMatches).catch(() => {}).finally(() => setLoading(false));
  }, [filter]);

  const columns: Column<Match>[] = [
    { key: "id", label: "ID", mono: true, render: (r) => <span className="font-mono text-xs" style={{ color: "var(--admin-dim)" }}>{String(r.id).slice(0, 8)}</span> },
    { key: "job_title", label: "Trabajo", render: (r) => <span style={{ fontWeight: 500 }}>{(r.job_title as string) || "—"}</span> },
    { key: "worker_name", label: "Trabajador", render: (r) => (r.worker_name as string) || "—" },
    { key: "status", label: "Estado", render: (r) => <StatusBadge status={r.status} type="match" /> },
    { key: "offered_rate", label: "Tarifa", mono: true, render: (r) => `Q${r.offered_rate}/día` },
  ];

  return (
    <div>
      <PageHeader title="Matches" />
      <div className="flex gap-2 mb-6 flex-wrap">
        {STATUS_FILTERS.map((f) => (
          <button key={f.value} onClick={() => setFilter(f.value)} className="rounded-full px-3 py-1.5 text-xs font-medium" style={{ background: filter === f.value ? "var(--admin-amber-bg)" : "var(--admin-surface)", border: `1px solid ${filter === f.value ? "var(--admin-amber-border)" : "var(--admin-border)"}`, color: filter === f.value ? "var(--admin-amber)" : "var(--admin-muted)" }}>
            {f.label}
          </button>
        ))}
      </div>
      <AdminTable columns={columns} data={matches} loading={loading} onRowClick={(r) => router.push(`/admin/matches/${r.id}`)} emptyMessage="No hay matches" />
    </div>
  );
}
