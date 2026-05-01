"use client";

import { useEffect, useState } from "react";
import PageHeader from "@/components/admin/PageHeader";
import AdminTable, { type Column } from "@/components/admin/AdminTable";
import StatusBadge from "@/components/admin/StatusBadge";
import {
  fetchConversations,
  resetConversation,
  approveWorkerConv,
  approveCompanyConv,
  adminSendWhatsApp,
} from "@/lib/admin-api";

interface Conv {
  id: string;
  phone: string;
  role: string | null;
  state: string;
  needs_human: boolean;
  worker_id: string | null;
  company_id: string | null;
  last_message_at: string;
  name: string;
  [key: string]: unknown;
}

const STATE_LABELS: Record<string, { label: string; color: "amber" | "green" | "blue" | "red" | "purple" | "gray" }> = {
  idle: { label: "📭 Sin actividad", color: "gray" },
  // Worker
  worker_ask_name: { label: "📝 Pidiendo nombre", color: "blue" },
  worker_ask_trade: { label: "📝 Pidiendo oficio", color: "blue" },
  worker_ask_experience: { label: "📝 Pidiendo experiencia", color: "blue" },
  worker_ask_zones: { label: "📝 Pidiendo zonas", color: "blue" },
  worker_ask_tools: { label: "📝 Pidiendo herramientas", color: "blue" },
  worker_ask_rate: { label: "📝 Pidiendo tarifa", color: "blue" },
  worker_ask_reference: { label: "📝 Pidiendo referencia", color: "blue" },
  worker_pending_approval: { label: "⏳ Esperando aprobación", color: "amber" },
  worker_active: { label: "✅ Activo", color: "green" },
  worker_paused: { label: "⏸️ Pausado", color: "amber" },
  // Company
  company_ask_name: { label: "🏢 Pidiendo nombre empresa", color: "blue" },
  company_ask_contact: { label: "🏢 Pidiendo contacto", color: "blue" },
  company_ask_email: { label: "🏢 Pidiendo email", color: "blue" },
  company_ask_type: { label: "🏢 Pidiendo tipo", color: "blue" },
  company_ask_zone: { label: "🏢 Pidiendo zona", color: "blue" },
  company_ask_nit: { label: "🏢 Pidiendo NIT", color: "blue" },
  company_pending_approval: { label: "⏳ Esperando aprobación", color: "amber" },
  company_active: { label: "✅ Activa", color: "green" },
  company_pending_match_decision: { label: "🤔 Decidiendo match", color: "purple" },
  // Job posting
  job_ask_trade: { label: "💼 Publicando trabajo", color: "purple" },
  job_ask_zone: { label: "💼 Publicando trabajo", color: "purple" },
  job_ask_dates: { label: "💼 Publicando trabajo", color: "purple" },
  job_ask_rate: { label: "💼 Publicando trabajo", color: "purple" },
  job_ask_tools: { label: "💼 Publicando trabajo", color: "purple" },
  job_ask_headcount: { label: "💼 Publicando trabajo", color: "purple" },
  job_ask_description: { label: "💼 Publicando trabajo", color: "purple" },
};

const FILTERS = [
  { value: "", label: "Todas" },
  { value: "role=worker", label: "Workers" },
  { value: "role=company", label: "Empresas" },
  { value: "state=worker_pending_approval", label: "Workers pendientes" },
  { value: "state=company_pending_approval", label: "Empresas pendientes" },
  { value: "needs_human=true", label: "Necesitan ayuda" },
];

export default function AdminWhatsAppPage() {
  const [convs, setConvs] = useState<Conv[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [msgTarget, setMsgTarget] = useState<string | null>(null);
  const [msgBody, setMsgBody] = useState("");

  const load = () => {
    setLoading(true);
    fetchConversations(filter).then(setConvs).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(load, [filter]);

  const total = convs.length;
  const workersPending = convs.filter((c) => c.state === "worker_pending_approval").length;
  const companiesPending = convs.filter((c) => c.state === "company_pending_approval").length;
  const needsHuman = convs.filter((c) => c.needs_human).length;

  const stateBadge = (state: string) => {
    const meta = STATE_LABELS[state] || { label: state, color: "gray" as const };
    return <StatusBadge status="" label={meta.label} color={meta.color} />;
  };

  const columns: Column<Conv>[] = [
    { key: "phone", label: "Teléfono", mono: true },
    { key: "name", label: "Nombre", render: (r) => r.name || "—" },
    { key: "role", label: "Rol", render: (r) => r.role === "worker" ? "👷 Worker" : r.role === "company" ? "🏢 Empresa" : "—" },
    { key: "state", label: "Estado", render: (r) => stateBadge(r.state) },
    { key: "last_message_at", label: "Última actividad", mono: true, render: (r) => new Date(r.last_message_at).toLocaleString("es-GT") },
    { key: "actions", label: "Acciones", render: (r) => (
      <div className="flex gap-1">
        {r.state === "worker_pending_approval" && (
          <button onClick={(e) => { e.stopPropagation(); approveWorkerConv(r.phone).then(load); }} className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>Aprobar</button>
        )}
        {r.state === "company_pending_approval" && (
          <button onClick={(e) => { e.stopPropagation(); approveCompanyConv(r.phone).then(load); }} className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-green-bg)", border: "1px solid var(--admin-green-border)", color: "var(--admin-green)" }}>Aprobar</button>
        )}
        <button onClick={(e) => { e.stopPropagation(); setMsgTarget(r.phone); setMsgBody(""); }} className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-blue-bg)", border: "1px solid var(--admin-blue-border)", color: "var(--admin-blue)" }}>Mensaje</button>
        <button onClick={(e) => { e.stopPropagation(); if (confirm("¿Resetear esta conversación a idle?")) resetConversation(r.phone).then(load); }} className="rounded px-2 py-1 text-xs font-medium" style={{ background: "var(--admin-amber-bg)", border: "1px solid var(--admin-amber-border)", color: "var(--admin-amber)" }}>Resetear</button>
      </div>
    )},
  ];

  return (
    <div>
      <PageHeader title="Conversaciones WhatsApp" subtitle="Phase 1 — todo el flujo via WhatsApp" />

      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total conversaciones", value: total, color: "var(--admin-blue)" },
          { label: "Workers pendientes", value: workersPending, color: "var(--admin-amber)" },
          { label: "Empresas pendientes", value: companiesPending, color: "var(--admin-amber)" },
          { label: "Necesitan ayuda humana", value: needsHuman, color: "var(--admin-red)" },
        ].map((s) => (
          <div key={s.label} className="rounded-xl p-5" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
            <p className="font-mono" style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</p>
            <p style={{ fontSize: 12, color: "var(--admin-muted)" }}>{s.label}</p>
          </div>
        ))}
      </div>

      <div className="flex gap-2 mb-4 flex-wrap">
        {FILTERS.map((f) => (
          <button key={f.value} onClick={() => setFilter(f.value)} className="rounded-full px-3 py-1.5 text-xs font-medium" style={{ background: filter === f.value ? "var(--admin-amber-bg)" : "var(--admin-surface)", border: `1px solid ${filter === f.value ? "var(--admin-amber-border)" : "var(--admin-border)"}`, color: filter === f.value ? "var(--admin-amber)" : "var(--admin-muted)" }}>
            {f.label}
          </button>
        ))}
      </div>

      <AdminTable columns={columns} data={convs} loading={loading} emptyMessage="No hay conversaciones aún." />

      {/* Send message modal */}
      {msgTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.4)" }} onClick={() => setMsgTarget(null)}>
          <div className="rounded-xl p-6 w-full max-w-md mx-4" style={{ background: "var(--admin-surface)" }} onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold mb-2" style={{ color: "var(--admin-text)" }}>Enviar WhatsApp a {msgTarget}</h3>
            <textarea value={msgBody} onChange={(e) => setMsgBody(e.target.value)} rows={5} className="w-full rounded-lg px-3 py-2 text-sm outline-none resize-none mb-3" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-text)" }} placeholder="Tu mensaje..." />
            <div className="flex justify-end gap-2">
              <button onClick={() => setMsgTarget(null)} className="rounded-lg px-4 py-2 text-sm" style={{ border: "1px solid var(--admin-border)", color: "var(--admin-muted)" }}>Cancelar</button>
              <button
                onClick={async () => { if (!msgBody.trim()) return; await adminSendWhatsApp(msgTarget!, msgBody); setMsgTarget(null); }}
                className="rounded-lg px-4 py-2 text-sm font-bold"
                style={{ background: "var(--admin-amber)", color: "#fff" }}
              >Enviar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
