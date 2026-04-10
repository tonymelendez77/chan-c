"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import { fetchAICalls } from "@/lib/admin-api";

interface AICall { id: string; worker_name: string; call_type: string; status: string; duration_seconds: number | null; created_at: string; [key: string]: unknown; }

const FILTERS = [
  { value: "", label: "Todas" },
  { value: "status=in_progress", label: "En curso" },
  { value: "status=completed", label: "Completadas" },
  { value: "status=failed", label: "Fallidas" },
];

export default function AICallsListPage() {
  const router = useRouter();
  const [calls, setCalls] = useState<AICall[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchAICalls(filter).then(setCalls).catch(() => {}).finally(() => setLoading(false));
  }, [filter]);

  const columns: Column<AICall>[] = [
    { key: "id", label: "ID", mono: true, render: (r) => <span className="font-mono text-xs" style={{ color: "var(--admin-dim)" }}>{String(r.id).slice(0, 8)}</span> },
    { key: "worker_name", label: "Trabajador", render: (r) => r.worker_name || "—" },
    { key: "call_type", label: "Tipo", render: (r) => <StatusBadge status={r.call_type} type="callType" /> },
    { key: "status", label: "Estado", render: (r) => <StatusBadge status={r.status} type="call" /> },
    { key: "duration_seconds", label: "Duración", mono: true, render: (r) => r.duration_seconds ? `${Math.floor(r.duration_seconds / 60)}:${String(r.duration_seconds % 60).padStart(2, "0")}` : "—" },
    { key: "created_at", label: "Fecha", mono: true, render: (r) => new Date(r.created_at).toLocaleDateString("es-GT") },
  ];

  return (
    <div>
      <PageHeader title="Llamadas IA" />
      <div className="flex gap-2 mb-6">
        {FILTERS.map((f) => (
          <button key={f.value} onClick={() => setFilter(f.value)} className="rounded-full px-3 py-1.5 text-xs font-medium" style={{ background: filter === f.value ? "var(--admin-amber-bg)" : "var(--admin-surface)", border: `1px solid ${filter === f.value ? "var(--admin-amber-border)" : "var(--admin-border)"}`, color: filter === f.value ? "var(--admin-amber)" : "var(--admin-muted)" }}>
            {f.label}
          </button>
        ))}
      </div>
      <AdminTable columns={columns} data={calls} loading={loading} onRowClick={(r) => router.push(`/admin/ai/calls/${r.id}`)} emptyMessage="No hay llamadas" />
    </div>
  );
}
