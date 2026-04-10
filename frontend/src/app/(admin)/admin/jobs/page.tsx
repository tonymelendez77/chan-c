"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import { fetchJobs } from "@/lib/admin-api";
import { TRADE_LABELS, type Job, type JobStatus } from "@/lib/types";

const JOB_STATUS_COLOR: Record<string, "blue" | "amber" | "green" | "gray" | "red"> = {
  draft: "gray", open: "blue", matching: "amber", filled: "green", completed: "gray", cancelled: "red",
};
const JOB_STATUS_LABEL: Record<string, string> = {
  draft: "Borrador", open: "Abierto", matching: "Buscando", filled: "Asignado", completed: "Completado", cancelled: "Cancelado",
};

export default function AdminJobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchJobs().then(setJobs).catch(() => {}).finally(() => setLoading(false)); }, []);

  const columns: Column<Job>[] = [
    { key: "id", label: "ID", mono: true, render: (r) => <span className="font-mono text-xs" style={{ color: "var(--admin-dim)" }}>{String(r.id).slice(0, 8)}</span> },
    { key: "title", label: "Título", render: (r) => <span style={{ fontWeight: 500 }}>{r.title}</span> },
    { key: "trade_required", label: "Oficio", render: (r) => <StatusBadge status="" label={TRADE_LABELS[r.trade_required]} color="blue" /> },
    { key: "zone", label: "Zona", render: (r) => `Zona ${r.zone}` },
    { key: "daily_rate", label: "Tarifa", mono: true, render: (r) => `Q${r.daily_rate}/día` },
    { key: "status", label: "Estado", render: (r) => <StatusBadge status="" label={JOB_STATUS_LABEL[r.status]} color={JOB_STATUS_COLOR[r.status]} /> },
    { key: "match_count", label: "Matches", mono: true, render: (r) => String(r.match_count ?? 0) },
  ];

  return (
    <div>
      <PageHeader title="Trabajos" />
      <AdminTable columns={columns} data={jobs} loading={loading} onRowClick={(r) => router.push(`/admin/jobs/${r.id}`)} emptyMessage="No hay trabajos registrados" />
    </div>
  );
}
