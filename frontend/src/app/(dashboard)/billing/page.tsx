"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import EmptyState from "@/components/ui/EmptyState";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import api from "@/lib/api";
import type { Payment } from "@/lib/types";

const fmtQ = (v: number | string | undefined) =>
  `Q${Number(v || 0).toLocaleString("es-GT", { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;

const STATUS_LABEL: Record<string, { label: string; color: string }> = {
  pending: { label: "Pendiente pago", color: "bg-amber-50 text-amber-700 border-amber-200" },
  invoiced: { label: "Facturada", color: "bg-blue-50 text-blue-700 border-blue-200" },
  paid: { label: "Pagada", color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  overdue: { label: "Vencida", color: "bg-red-50 text-red-700 border-red-200" },
};

export default function CompanyBillingPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/billing")
      .then((r) => setPayments(r.data))
      .catch(() => setPayments([]))
      .finally(() => setLoading(false));
  }, []);

  const totalPending = payments.filter((p) => p.status !== "paid").reduce((sum, p) => sum + Number(p.amount), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Facturación</h1>
        <p className="text-sm text-slate-500 mt-1">10% de comisión sobre el valor total de cada trabajo contratado</p>
      </div>

      <Card className="!bg-amber-50 !border-amber-200">
        <h3 className="font-semibold text-amber-900 mb-2">💡 Así funciona nuestra comisión</h3>
        <p className="text-sm text-amber-800 leading-relaxed">
          Ejemplo: Contratas un electricista a Q350/día por 5 días = Q1,750 de trabajo.
          CHAN-C cobra Q175 (10%) al confirmar el match.
          <br />
          <strong>Sin suscripciones. Sin cargos mensuales. Solo pagas cuando contratas.</strong>
        </p>
      </Card>

      {loading ? (
        <LoadingSpinner />
      ) : payments.length === 0 ? (
        <Card>
          <EmptyState
            title="Aún no tienes comisiones"
            description="Cuando contrates tu primer trabajador, verás el detalle aquí."
          />
        </Card>
      ) : (
        <>
          <Card className="!p-0 overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  {["Trabajo", "Trabajador", "Valor trabajo", "Comisión", "Estado", "Fecha"].map((h) => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {payments.map((p, i) => {
                  const s = STATUS_LABEL[p.status] || STATUS_LABEL.pending;
                  return (
                    <tr key={p.id} className={i < payments.length - 1 ? "border-b border-slate-100" : ""}>
                      <td className="px-4 py-3 text-sm font-medium text-slate-900">{p.job_title || "—"}</td>
                      <td className="px-4 py-3 text-sm text-slate-600">{p.worker_name || "—"}</td>
                      <td className="px-4 py-3 text-sm font-mono text-slate-900">{fmtQ(p.job_value)}</td>
                      <td className="px-4 py-3 text-sm font-mono font-semibold text-amber-700">{fmtQ(p.amount)}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${s.color}`}>{s.label}</span>
                      </td>
                      <td className="px-4 py-3 text-sm font-mono text-slate-500">
                        {p.invoice_date ? new Date(p.invoice_date).toLocaleDateString("es-GT") : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </Card>

          <Card className={totalPending > 0 ? "!border-amber-300" : "!border-emerald-300"}>
            <p className={`text-sm font-semibold ${totalPending > 0 ? "text-amber-700" : "text-emerald-700"}`}>
              Total pendiente: <span className="font-mono">{fmtQ(totalPending)}</span>
            </p>
          </Card>
        </>
      )}
    </div>
  );
}
