"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import TriggerButton from "@/components/admin/TriggerButton";
import { fetchRecruitmentPipeline, fetchPendingWorkers, triggerIntakeCalls, triggerReferenceCalls } from "@/lib/admin-api";

interface FunnelStats { sms_received: number; intake_calls_pending: number; intake_calls_completed: number; references_pending: number; pending_admin_review: number; approved_this_month: number; rejected_this_month: number; }
interface PendingWorker { id: string; full_name: string; phone: string; zone: string; created_at: string; initial_score: number | null; intake_completed: boolean; reference_count: number; [key: string]: unknown; }

export default function RecruitmentPage() {
  const router = useRouter();
  const [stats, setStats] = useState<FunnelStats | null>(null);
  const [workers, setWorkers] = useState<PendingWorker[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchRecruitmentPipeline(), fetchPendingWorkers()])
      .then(([s, w]) => { setStats(s); setWorkers(w); })
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const s = stats || { sms_received: 0, intake_calls_pending: 0, intake_calls_completed: 0, references_pending: 0, pending_admin_review: 0, approved_this_month: 0, rejected_this_month: 0 };

  const columns: Column<PendingWorker>[] = [
    { key: "full_name", label: "Nombre", render: (r) => <span style={{ fontWeight: 500 }}>{r.full_name}</span> },
    { key: "phone", label: "Teléfono", mono: true },
    { key: "initial_score", label: "Score", mono: true, render: (r) => r.initial_score !== null ? <span className="font-mono">{Number(r.initial_score).toFixed(2)}</span> : "—" },
    { key: "intake_completed", label: "Entrevista", render: (r) => r.intake_completed ? <StatusBadge status="" label="✓" color="green" /> : <StatusBadge status="" label="Pendiente" color="amber" /> },
    { key: "reference_count", label: "Refs", mono: true },
  ];

  return (
    <div>
      <PageHeader title="Pipeline de reclutamiento" />

      {/* Funnel stats */}
      <div className="grid grid-cols-3 xl:grid-cols-7 gap-3 mb-8">
        {[
          { label: "SMS recibidos", value: s.sms_received, color: "var(--admin-blue)" },
          { label: "Entrevistas pendientes", value: s.intake_calls_pending, color: "var(--admin-purple)" },
          { label: "Entrevistas completadas", value: s.intake_calls_completed, color: "var(--admin-green)" },
          { label: "Refs pendientes", value: s.references_pending, color: "var(--admin-amber)" },
          { label: "Revisión admin", value: s.pending_admin_review, color: "var(--admin-red)" },
          { label: "Aprobados mes", value: s.approved_this_month, color: "var(--admin-green)" },
          { label: "Rechazados mes", value: s.rejected_this_month, color: "var(--admin-dim)" },
        ].map((item) => (
          <div key={item.label} className="rounded-xl p-4" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <p className="font-mono" style={{ fontSize: 28, fontWeight: 700, color: item.color }}>{item.value}</p>
            <p style={{ fontSize: 11, color: "var(--admin-muted)" }}>{item.label}</p>
          </div>
        ))}
      </div>

      {/* Triggers */}
      <div className="grid grid-cols-2 gap-3 mb-8">
        <TriggerButton label="Procesar llamadas intake" subtitle={`${s.intake_calls_pending} pendientes`} onTrigger={triggerIntakeCalls} />
        <TriggerButton label="Procesar llamadas referencias" subtitle={`${s.references_pending} pendientes`} onTrigger={triggerReferenceCalls} />
      </div>

      <AdminTable columns={columns} data={workers} loading={loading} onRowClick={(r) => router.push(`/admin/workers/${r.id}`)} emptyMessage="No hay trabajadores en el pipeline" />
    </div>
  );
}
