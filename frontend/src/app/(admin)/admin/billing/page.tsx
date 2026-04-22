"use client";

import { useEffect, useState } from "react";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import { fetchBillingStats, fetchCommissions, markCommissionPaid } from "@/lib/admin-api";
import { TRADE_LABELS, type BillingStats, type Payment, type Trade } from "@/lib/types";

const fmtQ = (v: number | string | undefined) => {
  const n = typeof v === "number" ? v : Number(v || 0);
  return `Q ${n.toLocaleString("es-GT", { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
};

export default function AdminBillingPage() {
  const [stats, setStats] = useState<BillingStats | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([fetchBillingStats(), fetchCommissions()])
      .then(([s, p]) => { setStats(s); setPayments(p); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const totalPending = payments.filter((p) => p.status !== "paid").reduce((sum, p) => sum + Number(p.amount), 0);
  const totalCollectedMonth = stats?.commissions_collected ?? 0;

  const columns: Column<Payment>[] = [
    { key: "company_name", label: "Empresa", render: (r) => <span style={{ fontWeight: 500 }}>{r.company_name || "—"}</span> },
    { key: "worker_name", label: "Trabajador", render: (r) => r.worker_name || "—" },
    { key: "job_title", label: "Trabajo", render: (r) => (
      <div>
        <p>{r.job_title || "—"}</p>
        {r.trade && <span className="font-mono text-xs" style={{ color: "var(--admin-dim)" }}>{TRADE_LABELS[r.trade as Trade] || r.trade}</span>}
      </div>
    )},
    { key: "job_value", label: "Valor trabajo", mono: true, render: (r) => fmtQ(r.job_value) },
    { key: "amount", label: "Comisión (10%)", render: (r) => (
      <span className="font-mono" title={`${fmtQ(r.job_value)} × ${r.commission_pct}% = ${fmtQ(r.amount)}`} style={{ color: "var(--admin-amber)", fontWeight: 600 }}>{fmtQ(r.amount)}</span>
    )},
    { key: "status", label: "Estado", render: (r) => <StatusBadge status={r.status} type="payment" /> },
    { key: "invoice_date", label: "Fecha", mono: true, render: (r) => r.invoice_date ? new Date(r.invoice_date).toLocaleDateString("es-GT") : "—" },
    { key: "actions", label: "Acciones", render: (r) => r.status !== "paid" ? (
      <button onClick={() => markCommissionPaid(r.id).then(load)} className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>Marcar pagada</button>
    ) : <span style={{ fontSize: 11, color: "var(--admin-dim)" }}>—</span> },
  ];

  return (
    <div>
      <PageHeader title="Comisiones — 10% por trabajo" subtitle="Comisión automática calculada al aceptar cada match" />

      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "Pendientes", value: fmtQ(stats?.commissions_pending), color: "var(--admin-amber)", sub: `${payments.filter((p) => p.status !== "paid").length} comisiones sin cobrar` },
          { label: "Cobradas este mes", value: fmtQ(totalCollectedMonth), color: "var(--admin-green)", sub: `${payments.filter((p) => p.status === "paid").length} comisiones pagadas` },
          { label: "Valor total de trabajos activos", value: fmtQ(stats?.total_job_value_active), color: "var(--admin-blue)", sub: "Valor bruto en curso" },
          { label: "Comisión promedio", value: fmtQ(stats?.average_commission), color: "var(--admin-purple)", sub: "Por placement este mes" },
        ].map((s) => (
          <div key={s.label} className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <p className="font-mono" style={{ fontSize: 26, fontWeight: 700, color: s.color, lineHeight: 1 }}>{s.value}</p>
            <p className="mt-2" style={{ fontSize: 13, fontWeight: 500, color: "var(--admin-text)" }}>{s.label}</p>
            <p style={{ fontSize: 11, color: "var(--admin-muted)" }}>{s.sub}</p>
          </div>
        ))}
      </div>

      <AdminTable columns={columns} data={payments} loading={loading} emptyMessage="No hay comisiones registradas. Se generarán automáticamente al aceptar cada match." />

      {payments.length > 0 && (
        <div className="mt-4 rounded-xl p-4 flex justify-between" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
          <span className="font-mono" style={{ fontSize: 14, fontWeight: 600, color: "var(--admin-amber)" }}>Total pendiente: {fmtQ(totalPending)}</span>
          <span className="font-mono" style={{ fontSize: 14, fontWeight: 600, color: "var(--admin-green)" }}>Total cobrado este mes: {fmtQ(totalCollectedMonth)}</span>
        </div>
      )}
    </div>
  );
}
