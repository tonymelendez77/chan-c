"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import { fetchWorkers } from "@/lib/admin-api";
import { TRADE_LABELS, type Worker } from "@/lib/types";

export default function AdminWorkersPage() {
  const router = useRouter();
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchWorkers().then(setWorkers).catch(() => {}).finally(() => setLoading(false)); }, []);

  const columns: Column<Worker>[] = [
    { key: "full_name", label: "Nombre", render: (r) => (
      <div className="flex items-center gap-2.5">
        <div className="flex items-center justify-center rounded-lg text-white text-xs font-bold" style={{ width: 32, height: 32, background: r.is_active ? "var(--admin-green)" : "var(--admin-dim)" }}>{r.full_name.charAt(0)}</div>
        <span style={{ fontWeight: 500 }}>{r.full_name}</span>
      </div>
    )},
    { key: "phone", label: "Teléfono", mono: true },
    { key: "zone", label: "Zona", render: (r) => r.zone ? `Zona ${r.zone}` : "—" },
    { key: "trades", label: "Oficio", render: (r) => r.trades?.[0] ? <StatusBadge status="" label={TRADE_LABELS[r.trades[0].trade]} color="blue" /> : "—" },
    { key: "rating_avg", label: "Rating", mono: true, render: (r) => <span>★ {Number(r.rating_avg).toFixed(1)}</span> },
    { key: "total_jobs", label: "Trabajos", mono: true },
    { key: "is_active", label: "Estado", render: (r) =>
      (r as Worker & { paused?: boolean }).paused ? <StatusBadge status="" label="⏸️ Pausado" color="amber" /> :
      r.is_active && r.is_vetted ? <StatusBadge status="" label="Activo" color="green" /> :
      r.is_active ? <StatusBadge status="" label="Sin vetar" color="amber" /> :
      <StatusBadge status="" label="Inactivo" color="red" />
    },
  ];

  return (
    <div>
      <PageHeader title="Pool de trabajadores" subtitle={`${workers.length} trabajadores`} />
      <AdminTable columns={columns} data={workers} loading={loading} onRowClick={(r) => router.push(`/admin/workers/${r.id}`)} emptyMessage="No hay trabajadores registrados" />
    </div>
  );
}
