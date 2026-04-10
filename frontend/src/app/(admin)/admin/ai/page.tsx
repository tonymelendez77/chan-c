"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import TriggerButton from "@/components/admin/TriggerButton";
import { fetchAICalls, triggerAICalls, processCompletedCalls } from "@/lib/admin-api";

interface AICall { id: string; worker_name: string; worker_phone: string; call_type: string; status: string; duration_seconds: number | null; created_at: string; vapi_call_id: string | null; [key: string]: unknown; }

export default function AIPipelinePage() {
  const router = useRouter();
  const [calls, setCalls] = useState<AICall[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchAICalls().then(setCalls).catch(() => {}).finally(() => setLoading(false)); }, []);

  const columns: Column<AICall>[] = [
    { key: "id", label: "ID", mono: true, render: (r) => <span className="font-mono text-xs" style={{ color: "var(--admin-dim)" }}>{String(r.id).slice(0, 8)}</span> },
    { key: "worker_name", label: "Trabajador", render: (r) => <span style={{ fontWeight: 500 }}>{r.worker_name || "—"}</span> },
    { key: "call_type", label: "Tipo", render: (r) => <StatusBadge status={r.call_type} type="callType" /> },
    { key: "status", label: "Estado", render: (r) => <StatusBadge status={r.status} type="call" /> },
    { key: "duration_seconds", label: "Duración", mono: true, render: (r) => r.duration_seconds ? `${Math.floor(r.duration_seconds / 60)}:${String(r.duration_seconds % 60).padStart(2, "0")}` : "—" },
    { key: "created_at", label: "Fecha", mono: true, render: (r) => new Date(r.created_at).toLocaleDateString("es-GT") },
  ];

  return (
    <div>
      <PageHeader title="Pipeline de IA" />

      <div className="rounded-xl p-5 mb-8" style={{ background: "var(--admin-amber-bg)", border: "1px solid var(--admin-amber-border)" }}>
        <p className="mb-4" style={{ fontSize: 14, fontWeight: 600, color: "var(--admin-amber)" }}>Controles del pipeline</p>
        <div className="grid grid-cols-2 gap-3">
          <TriggerButton label="Disparar llamadas pendientes" subtitle="Matches esperando llamada IA" onTrigger={triggerAICalls} />
          <TriggerButton label="Procesar llamadas completadas" subtitle="Transcripciones pendientes de extracción" onTrigger={processCompletedCalls} />
        </div>
      </div>

      <AdminTable columns={columns} data={calls} loading={loading} onRowClick={(r) => router.push(`/admin/ai/calls/${r.id}`)} emptyMessage="No hay llamadas IA registradas" />
    </div>
  );
}
