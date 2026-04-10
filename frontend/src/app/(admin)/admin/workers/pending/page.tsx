"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import { fetchPendingWorkers, approveWorker, rejectWorker } from "@/lib/admin-api";

interface PendingWorker { id: string; full_name: string; phone: string; zone: string; language: string; created_at: string; initial_score: number | null; intake_completed: boolean; reference_count: number; [key: string]: unknown; }

export default function PendingWorkersPage() {
  const router = useRouter();
  const [workers, setWorkers] = useState<PendingWorker[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => { setLoading(true); fetchPendingWorkers().then(setWorkers).catch(() => {}).finally(() => setLoading(false)); };
  useEffect(load, []);

  const columns: Column<PendingWorker>[] = [
    { key: "full_name", label: "Nombre", render: (r) => <span style={{ fontWeight: 500 }}>{r.full_name}</span> },
    { key: "phone", label: "Teléfono", mono: true },
    { key: "zone", label: "Zona", render: (r) => r.zone || "—" },
    { key: "initial_score", label: "Score", mono: true, render: (r) => {
      const s = r.initial_score;
      if (s === null) return "—";
      const color = s >= 0.7 ? "green" : s >= 0.5 ? "amber" : "red";
      return <StatusBadge status="" label={s.toFixed(2)} color={color} />;
    }},
    { key: "intake_completed", label: "Entrevista", render: (r) => r.intake_completed ? <StatusBadge status="" label="Completada" color="green" /> : <StatusBadge status="" label="Pendiente" color="amber" /> },
    { key: "reference_count", label: "Refs", mono: true },
    { key: "actions", label: "Acciones", render: (r) => (
      <div className="flex gap-1">
        <button onClick={(e) => { e.stopPropagation(); approveWorker(r.id).then(load); }} className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>Aprobar</button>
        <button onClick={(e) => { e.stopPropagation(); rejectWorker(r.id).then(load); }} className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-red-bg)", border: "1px solid var(--admin-red-border)", color: "var(--admin-red)" }}>Rechazar</button>
      </div>
    )},
  ];

  return (
    <div>
      <PageHeader title="Trabajadores pendientes de aprobación" subtitle={`${workers.length} pendientes`} />
      <AdminTable columns={columns} data={workers} loading={loading} onRowClick={(r) => router.push(`/admin/workers/${r.id}`)} emptyMessage="No hay trabajadores pendientes" />
    </div>
  );
}
