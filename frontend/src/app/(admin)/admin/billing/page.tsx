"use client";

import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";

export default function BillingPage() {
  return (
    <div>
      <PageHeader title="Comisiones e ingresos" />

      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "Pendientes este mes", value: "Q 0", color: "var(--admin-amber)" },
          { label: "Cobradas este mes", value: "Q 0", color: "var(--admin-green)" },
          { label: "Total histórico", value: "Q 0", color: "var(--admin-blue)" },
          { label: "Empresas con deuda", value: "0", color: "var(--admin-red)" },
        ].map((s) => (
          <div key={s.label} className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <p className="font-mono" style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</p>
            <p style={{ fontSize: 12, color: "var(--admin-muted)" }}>{s.label}</p>
          </div>
        ))}
      </div>

      <AdminTable columns={[]} data={[]} emptyMessage="No hay pagos registrados. Las comisiones se generarán cuando se completen matches." />
    </div>
  );
}
